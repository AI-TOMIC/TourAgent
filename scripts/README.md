# Scripts 폴더

서울시 기상 데이터 수집 스크립트들

## 파일 설명

### 🔧 weather_utils.py
기상청 업데이트 시간 계산 유틸리티
```python
from weather_utils import get_latest_update_datetime
latest_time = get_latest_update_datetime()
```

### 🗺️ geo_processor.py  
지리 데이터 처리 및 좌표 변환
```python
from geo_processor import load_and_process_location_data, match_coordinates
location_df, region_gdf = load_and_process_location_data()
result_df = match_coordinates(location_df, region_gdf)
```

### 🌤️ weather_api.py
기상청 API 호출 및 데이터 수집
```python
from weather_api import WeatherAPI
api = WeatherAPI()
weather_data = api.collect_all_weather_data(location_df)
```

### ▶️ main.py
전체 프로세스 실행
```bash
python main.py
```

## 실행 순서

1. `weather_utils.py` → 최신 업데이트 시간 계산
2. `geo_processor.py` → 지리 데이터 로드 및 좌표 매칭  
3. `weather_api.py` → 기상 데이터 수집
4. `main.py` → 전체 통합 실행 및 저장

## 필요한 데이터 파일

상위 폴더의 `data/` 디렉토리에 다음 파일들이 필요합니다:
- 서울시 주요 120장소 영역.cpg
- 서울시 주요 120장소 영역.dbf
- 서울시 주요 120장소 영역.prj
- 서울시 주요 120장소 영역.qmd
- 서울시 주요 120장소 영역.shp
- 서울시 주요 120장소 영역.shx
- 기상청41_단기예보 조회서비스_오픈API활용가이드_격자_위경도.xlsx  
- 서울시 주요 120장소 목록.xlsx