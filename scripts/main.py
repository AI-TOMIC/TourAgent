"""메인 실행 파일"""

import pandas as pd
from geo_processor import load_and_process_location_data, match_coordinates
from weather_api import WeatherAPI

def main():
    """메인 실행 함수"""
    
    print("=== 서울시 주요 관광지 기상 데이터 수집 시작 ===")
    
    # 1. 지리 데이터 로드 및 처리
    print("\n1. 지리 데이터 로드 중...")
    merged_df, seoul_region_gdf = load_and_process_location_data()
    
    # 2. 좌표 매칭
    print("\n2. 기상청 격자 좌표 매칭 중...")
    location_data = match_coordinates(merged_df, seoul_region_gdf)
    
    # 3. 기상 데이터 수집
    print("\n3. 기상 데이터 수집 중...")
    weather_api = WeatherAPI()
    all_dfs = weather_api.collect_all_weather_data(location_data)
    
    # 4. 결과 저장
    if all_dfs:
        weather_all = pd.concat(all_dfs, ignore_index=True)
        weather_all.to_csv("../data/processed/weather_data_all.csv", index=False, encoding="utf-8-sig")
        print(f"\n=== 수집 완료: {weather_all.shape[0]}행 × {weather_all.shape[1]}열 ===")
        print("파일 저장 위치: ../data/processed/weather_data_all.csv")
    else:
        print("\n=== 수집된 데이터가 없습니다 ===")

if __name__ == "__main__":
    main()