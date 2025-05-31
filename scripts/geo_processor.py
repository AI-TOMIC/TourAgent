"""지리 데이터 처리 모듈"""

import geopandas as gpd
import pandas as pd
import numpy as np

def load_and_process_location_data():
    """지리 데이터를 로드하고 처리합니다."""
    
    # 1. Shapefile 로드
    shapefile_path = "../data/raw/서울시 주요 120장소 영역.shp"
    gdf = gpd.read_file(shapefile_path)
    
    # 중심점 계산
    gdf['centroid_x'] = gdf.geometry.centroid.x
    gdf['centroid_y'] = gdf.geometry.centroid.y
    gdf = gdf.to_crs(epsg=4326)
    
    # 2. 기상청 격자 데이터 로드
    region = pd.read_excel("../data/raw/기상청41_단기예보 조회서비스_오픈API활용가이드_격자_위경도.xlsx")
    seoul_region = region[region.loc[:, '1단계'] == '서울특별시']
    seoul_region['시구동'] = seoul_region[['1단계', '2단계', '3단계']].fillna("").agg(" ".join, axis=1)
    
    seoul_region_gdf = gpd.GeoDataFrame(
        seoul_region, 
        geometry=gpd.points_from_xy(
            seoul_region.loc[:,'경도(초/100)'], 
            seoul_region.loc[:,'위도(초/100)'], 
            crs='epsg:4326'
        )
    )
    
    seoul_region_gdf = seoul_region_gdf.rename(columns={
        "경도(초/100)": "lon",
        "위도(초/100)": "lat"
    })
    
    # 3. 관광지 목록 로드 및 병합
    tour_list = pd.read_excel('../data/raw/서울시 주요 120장소 목록.xlsx')
    merged_df = pd.merge(tour_list, gdf, how='left')
    
    return merged_df, seoul_region_gdf

def match_coordinates(merged_df, seoul_region_gdf):
    """각 관광지에 가장 가까운 기상청 격자 좌표를 매칭합니다."""
    
    merged_df['시구동'] = ''
    merged_df['nx'] = ''
    merged_df['ny'] = ''

    for i in range(len(merged_df)):
        print(f"좌표 매칭 중... {i+1}/{len(merged_df)}")
        
        euclidean_distances = np.sqrt(
            np.power(seoul_region_gdf.lon - merged_df.iloc[i].centroid_x, 2) + 
            np.power(seoul_region_gdf.lat - merged_df.iloc[i].centroid_y, 2)
        )
        argmin_idx = euclidean_distances.argmin()

        merged_df.loc[i, '시구동'] = seoul_region_gdf.iloc[argmin_idx]['시구동']
        merged_df.loc[i, 'nx'] = seoul_region_gdf.iloc[argmin_idx]['격자 X']
        merged_df.loc[i, 'ny'] = seoul_region_gdf.iloc[argmin_idx]['격자 Y']
    
    return merged_df