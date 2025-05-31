# TourAgent

## 개요

## 환경세팅(나중에 지워도 됨)
![image](https://github.com/user-attachments/assets/0fe2848a-d758-44dc-96e8-d18e29287e23)
아래 추가된 내용
![image](https://github.com/user-attachments/assets/ac0cd73c-35d3-47ef-b407-b720ba92aa27)


# 기상 데이터 수집 스크립트

서울시 주요 120장소의 기상 데이터를 수집하는 스크립트입니다.

## 파일 구조

```
scripts/
├── weather_utils.py      # 시간 계산 유틸리티
├── geo_processor.py      # 지리 데이터 처리
├── weather_api.py        # 기상청 API 호출
└── main.py               # 메인 실행 파일
```

## 사용법

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경변수 설정
```bash
# .env 파일에 기상청 API 키 입력
WEATHER_API_DECODING=your_api_key_here
```

### 3. 실행
```bash
cd scripts
python main.py
```

## 필요한 데이터 파일

`data/raw/` 폴더에 다음 파일들이 필요합니다:
- `서울시 주요 120장소 영역.cpg`
- `서울시 주요 120장소 영역.dbf`
- `서울시 주요 120장소 영역.prj`
- `서울시 주요 120장소 영역.qmd`
- `서울시 주요 120장소 영역.shp`
- `서울시 주요 120장소 영역.shx`
- `기상청41_단기예보 조회서비스_오픈API활용가이드_격자_위경도.xlsx`
- `서울시 주요 120장소 목록.xlsx`

## 출력

- **파일**: `weather_data_all.csv`
- **데이터**: 기온, 습도, 강수확률, 풍속 등 기상 정보
- **형식**: 지역별 시간대별 기상 데이터

## API 키 발급

[공공데이터포털](https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15084084)에서 '단기예보 조회' 활용신청