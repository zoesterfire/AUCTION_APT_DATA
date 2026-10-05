import os
import datetime
import requests
from PublicDataReader import TransactionPrice

# 1. 숨겨둔 비밀번호 불러오기
SERVICE_KEY = os.environ.get("SERVICE_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

api = TransactionPrice(SERVICE_KEY)
now_ym = datetime.datetime.now().strftime("%Y%m")

# 2. 체크하고 싶은 아파트 정보 목록 (주소지 모음)
targets = [
    {"name": "소래마을풍림", "sigungu": "28200", "area": 59}, # 인천 남동구
    {"name": "동남디아망", "sigungu": "28260", "area": 84},   # 인천 서구
    {"name": "한양", "sigungu": "28177", "area": 84},         # 인천 미추홀구
    {"name": "솔밭마을", "sigungu": "28185", "area": 49},     # 인천 연수구
    {"name": "현대", "sigungu": "28245", "area": 84},         # 인천 계양구
    # 더 추가하고 싶은 단지가 있다면 이어서 적으면 돼요!
]

results = ["📊 **오늘의 실거래가 체크 결과**\n"]

for t in targets:
    try:
        df = api.get_data(
            property_type="아파트", 
            trade_type="매매", 
            sigungu_code=t["sigungu"], 
            year_month=now_ym
        )
        if not df.empty:
            # 아파트명과 전용면적이 일치하는 거래가 있는지 확인
            matched = df[(df['아파트'] == t['name']) & (df['전용면적'].astype(float).astype(int) == t['area'])]
            if not matched.empty:
                for _, row in matched.iterrows():
                    results.append(f"✅ [{t['name']}] {row['전용면적']}㎡ | {row['층']}층 | {row['거래금액']}만원")
    except Exception as e:
        pass

# 3. 결과 메시지 정리 후 텔레그램으로 쏘기!
if len(results) == 1:
    message = "오늘 새로 등록된 실거래가가 없어요! 😴"
else:
    message = "\n".join(results)

url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
requests.post(url, data={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"})
