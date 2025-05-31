"""기상 데이터 수집 유틸리티 함수들"""

from bisect import bisect_right
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

def get_latest_update_datetime():
    """최신 기상 업데이트 시간을 계산합니다."""
    update_hours = [2, 5, 8, 11, 14, 17, 20, 23]
    now = datetime.now()
    i = bisect_right(update_hours, now.hour)

    if i > 0:
        # 같은 날에 업데이트 된 마지막 시간
        selected_hour = update_hours[i - 1]
        selected_date = now.date()
    else:
        # 아직 오늘 첫 업데이트(02시) 전에 요청한 경우, 전날 23시
        selected_hour = update_hours[-1]
        selected_date = now.date() - timedelta(days=1)

    # 최종 datetime 객체 생성
    return datetime(
        year=selected_date.year,
        month=selected_date.month,
        day=selected_date.day,
        hour=selected_hour
    )