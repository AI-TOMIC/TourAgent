from bisect import bisect_right
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore') # warning message 제거

# 1) 업데이트 시간 목록
update_hours = [2, 5, 8, 11, 14, 17, 20, 23]

def get_latest_update_datetime():
    now = datetime.now()  # 현재 로컬 시각 취득 :contentReference[oaicite:5]{index=5}
    i = bisect_right(update_hours, now.hour)  # 삽입 인덱스 계산 :contentReference[oaicite:6]{index=6}

    if i > 0:
        # 같은 날에 업데이트 된 마지막 시간
        selected_hour = update_hours[i - 1]
        selected_date = now.date()
    else:
        # 아직 오늘 첫 업데이트(02시) 전에 요청한 경우, 전날 23시
        selected_hour = update_hours[-1]
        selected_date = now.date() - timedelta(days=1)  # 하루 뺌 :contentReference[oaicite:7]{index=7}

    # 최종 datetime 객체 생성
    return datetime(
        year=selected_date.year,
        month=selected_date.month,
        day=selected_date.day,
        hour=selected_hour
    )


latest_dt = get_latest_update_datetime()
BASE_DATE = latest_dt.strftime("%Y%m%d") # 0200, 0500, 0800, 1100, 1400, 1700, 2000, 2300
BASE_TIME = latest_dt.strftime("%H00")

import geopandas as gpd

shapefile_path = "./data/shape/서울시 주요 120장소 영역.shp"

gdf = gpd.read_file(shapefile_path)

gdf['centroid_x'] = gdf.geometry.centroid.x
gdf['centroid_y'] = gdf.geometry.centroid.y

gdf = gdf.to_crs(epsg=4326)

import pandas as pd

region = pd.read_excel("./data/기상청41_단기예보 조회서비스_오픈API활용가이드_격자_위경도.xlsx")

seoul_region = region[region.loc[:, '1단계'] == '서울특별시']

seoul_region['시구동'] = seoul_region[['1단계', '2단계', '3단계']].fillna("").agg(" ".join, axis=1)

seoul_region_gdf = gpd.GeoDataFrame(seoul_region, geometry=gpd.points_from_xy(seoul_region.loc[:,'경도(초/100)'], seoul_region.loc[:,'위도(초/100)'], crs='epsg:4326'))

seoul_region_gdf = seoul_region_gdf.rename(columns={
    "경도(초/100)": "lon",
    "위도(초/100)": "lat"
})

tour_list = pd.read_excel('./data/서울시 주요 120장소 목록.xlsx')
merged_df = pd.merge(tour_list, gdf, how='left')

import numpy as np

# 반복문으로 실행

merged_df['시구동'] = ''
merged_df['nx'] = ''
merged_df['ny'] = ''

for i in range(len(merged_df)):
    print(i)
    euclidean_distances = np.sqrt(np.power(seoul_region_gdf.lon - merged_df.iloc[i].centroid_x, 2) + np.power(seoul_region_gdf.lat - merged_df.iloc[i].centroid_y, 2))
    argmin_idx = euclidean_distances.argmin()

    merged_df.loc[i, '시구동'] = seoul_region_gdf.iloc[argmin_idx]['시구동']
    merged_df.loc[i, 'nx'] = seoul_region_gdf.iloc[argmin_idx]['격자 X']
    merged_df.loc[i, 'ny'] = seoul_region_gdf.iloc[argmin_idx]['격자 Y']


import os, requests
from datetime import datetime
from dotenv import load_dotenv
import time

# .env 파일 로드
load_dotenv()
WEATHER_API = os.getenv("WEATHER_API_DECODING")

MAX_RETRIES = 5 # 오류시, 재시도 횟수
RETRY_DELAY = 1 # 초 단위


all_dfs = []
i = 1

url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"

for _, row in merged_df.iterrows():

    nx = int(row['nx'])
    ny = int(row['ny'])
    area = row["AREA_NM"]

    print(area, " 시작!")

    params = {
        'serviceKey': WEATHER_API,
        'pageNo': 1,
        'numOfRows': 10000,
        'dataType':'JSON', #XML
        'base_date': BASE_DATE,
        'base_time': BASE_TIME,
        'nx': nx,
        'ny': ny
        }
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(url, params=params, timeout=50)
            resp.raise_for_status()
            items = resp.json()['response']['body']['items']['item']
            print(f"{area} 완료! (시도 {attempt})")
            break # 성공하면 재시도 루프 탈출
        except (requests.exceptions.RequestException, ValueError) as e:
            print(f"{area} 요청 실패: {e} (시도 {attempt})")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                print(f"{area} 최대 재시도 횟수({MAX_RETRIES}) 초과, 건더뜁니다.")
                items = [] # 아이템 없다고 처리
        
    # items 처리
    if not items:
        continue
            
    df = pd.json_normalize(items, meta=['baseDate', 'baseTime'], errors='ignore')

    df['AREA_NM'] = area
    all_dfs.append(df)

    print(f"{i}/{len(merged_df)}")
    i += 1
    time.sleep(0.5)


weather_all = pd.concat(all_dfs, ignore_index=True)
weather_all.to_csv("./weather_data_all.csv", index=False, encoding="utf-8-sig")

'''
◼ +900이상, –900 이하 값은 Missing 값으로 처리
관측장비가 없는 해양 지역이거나 관측장비의 결측 등으로 자료가 없음을 의미
◼ 압축 Bit 수의 경우 Missing 값이 아닌 경우의 기준

- 하늘상태(SKY) 코드 : 맑음(1), 구름많음(3), 흐림(4)
- 강수형태(PTY) 코드 : (초단기) 없음(0), 비(1), 비/눈(2), 눈(3), 빗방울(5), 빗방울눈날림(6), 눈날림(7) 
                      (단기) 없음(0), 비(1), 비/눈(2), 눈(3), 소나기(4) 

- 풍속 정보
동서바람성분(UUU) : 동(+표기), 서(-표기)
남북바람성분(VVV) : 북(+표기), 남(-표기)

20250528,2300,TMP,20250529,0000,17,61,125
20250528,2300,UUU,20250529,0000,-0.8,61,125
20250528,2300,VVV,20250529,0000,-0.1,61,125
20250528,2300,VEC,20250529,0000,83,61,125
20250528,2300,WSD,20250529,0000,0.9,61,125
20250528,2300,SKY,20250529,0000,1,61,125
20250528,2300,PTY,20250529,0000,0,61,125
20250528,2300,POP,20250529,0000,0,61,125
20250528,2300,WAV,20250529,0000,-999,61,125
20250528,2300,PCP,20250529,0000,강수없음,61,125
20250528,2300,REH,20250529,0000,85,61,125
20250528,2300,SNO,20250529,0000,적설없음,61,125

항목값	항목명	        단위	    압축bit수
POP	    강수확률	    %	        8
PTY	    강수형태	    코드값	    4
PCP	    1시간 강수량	범주 (1 mm)	8
REH	    습도	        %	       8
SNO	    1시간 신적설	범주(1 cm)	8
SKY	    하늘상태	    코드값	    4
TMP	    1시간 기온	    ℃	      10
TMN	    일 최저기온	    ℃	      10
TMX	    일 최고기온	    ℃	      10
UUU	    풍속(동서성분)	m/s	       12
VVV	    풍속(남북성분)	m/s	       12
WAV	    파고	        M	      8
VEC	    풍향	        deg	      10
WSD	    풍속	        m/s	      10

'''