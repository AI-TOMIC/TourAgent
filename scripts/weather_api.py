"""기상청 API 호출 모듈"""

import os
import requests
import pandas as pd
import time
from dotenv import load_dotenv, find_dotenv
from weather_utils import get_latest_update_datetime

# 환경변수 로드 - 프로젝트 어디서든 .env 파일을 자동으로 찾음
load_dotenv(find_dotenv())

class WeatherAPI:
    def __init__(self):
        self.api_key = os.getenv("WEATHER_API_DECODING")
        self.url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
        self.max_retries = 5
        self.retry_delay = 1
        
    def get_weather_data(self, nx, ny, area_name):
        """특정 지역의 기상 데이터를 가져옵니다."""
        
        latest_dt = get_latest_update_datetime()
        base_date = latest_dt.strftime("%Y%m%d")
        base_time = latest_dt.strftime("%H00")
        
        params = {
            'serviceKey': self.api_key,
            'pageNo': 1,
            'numOfRows': 10000,
            'dataType': 'JSON',
            'base_date': base_date,
            'base_time': base_time,
            'nx': nx,
            'ny': ny
        }
        
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = requests.get(self.url, params=params, timeout=50)
                resp.raise_for_status()
                
                response_data = resp.json()
                
                # 응답 구조 확인 및 데이터 존재 여부 체크
                if ('response' not in response_data or 
                    'body' not in response_data['response'] or 
                    'items' not in response_data['response']['body']):
                    print(f"{area_name} → 응답 구조가 올바르지 않음, 건너뜀")
                    return None
                    
                items_data = response_data['response']['body']['items']
                
                # items가 빈 값이거나 item 키가 없는 경우 처리
                if not items_data or 'item' not in items_data:
                    print(f"{area_name} → 데이터 없음, 건너뜀")
                    return None
                    
                items = items_data['item']
                
                # items가 빈 리스트인 경우도 처리
                if not items:
                    print(f"{area_name} → 빈 데이터, 건너뜀")
                    return None
                
                print(f"{area_name} 완료! (시도 {attempt})")
                return items
                
            except (requests.exceptions.RequestException, ValueError) as e:
                print(f"{area_name} 요청 실패: {e} (시도 {attempt})")
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
                else:
                    print(f"{area_name} 최대 재시도 횟수({self.max_retries}) 초과, 건너뜁니다.")
                    return None
        
        return None
    
    def collect_all_weather_data(self, location_df):
        """모든 지역의 기상 데이터를 수집합니다."""
        
        all_dfs = []
        
        for i, (_, row) in enumerate(location_df.iterrows(), 1):
            nx = int(row['nx'])
            ny = int(row['ny'])
            area = row["AREA_NM"]
            
            print(f"{area} 시작! ({i}/{len(location_df)})")
            
            items = self.get_weather_data(nx, ny, area)
            
            if items:
                # dict 또는 list 형태 처리
                if isinstance(items, dict):
                    df = pd.json_normalize([items])
                else:
                    df = pd.json_normalize(items)
                
                df['AREA_NM'] = area
                all_dfs.append(df)
            
            time.sleep(0.5)  # API 호출 간격 조절
        
        return all_dfs