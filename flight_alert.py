"""
대한항공 인천(ICN) → LA(LAX) 2027-02-05 출발 최저가를 조회해서 이메일로 보내는 스크립트
- 가격 데이터: Ignav API (https://ignav.com)
- 메일 발송: Gmail SMTP (앱 비밀번호 사용)
"""
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timezone, timedelta

import requests

# ===== 조회 조건 (필요하면 여기만 바꾸세요) =====
ORIGIN = "ICN"
DESTINATION = "LAX"
DEPARTURE_DATE = "2027-02-05"
AIRLINE = "KE"          # 대한항공
NONSTOP_ONLY = True     # 직항만 보기

# ===== 환경변수 (GitHub Secrets에 저장) =====
IGNAV_API_KEY = os.environ["IGNAV_API_KEY"]
GMAIL_ADDRESS = os.environ["GMAIL_ADDRESS"]        # 보내는 Gmail 주소
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
TO_EMAIL = os.environ.get("TO_EMAIL", GMAIL_ADDRESS)  # 받을 주소 (없으면 본인에게)

KST = timezone(timedelta(hours=9))


def search_fares():
    body = {
        "origin": ORIGIN,
        "destination": DESTINATION,
        "departure_date": DEPARTURE_DATE,
        "airlines_include": [AIRLINE],
        "market": "KR",
    }
    if NONSTOP_ONLY:
        body["max_stops"] = 0

    res = requests.post(
        "https://ignav.com/api/fares/one-way",
        headers={"X-Api-Key": IGNAV_API_KEY, "Content-Type": "application/json"},
        json=body,
        timeout=60,
    )
    res.raise_for_status()
    return res.json().get("itineraries", [])


def describe(it):
    price = it["price"]
    seg = it["outbound"]["segments"][0]
    dep = seg["departure_time_local"][11:16]
    arr = seg["arrival_time_local"][11:16]
    flight = f'{seg["marketing_carrier_code"]}{seg["flight_number"]}'
    note = "" if price.get("status") == "verified" else " (미확인 가격)"
    return f'{flight}  {dep} 출발 → {arr} 도착  |  {price["amount"]:,.0f} {price["currency"]}{note}'


def build_message(itineraries):
    today = datetime.now(KST).strftime("%Y-%m-%d")
    header = f"[{today}] 대한항공 {ORIGIN}→{DESTINATION} {DEPARTURE_DATE} 출발 가격\n\n"

    valid = [i for i in itineraries if i["price"]["amount"] > 0]
    if not valid:
        return "항공권 가격: 조회 결과 없음", header + "오늘은 조회된 항공편이 없어요."

    valid.sort(key=lambda i: i["price"]["amount"])
    cheapest = valid[0]["price"]
    subject = f'✈️ 대한항공 LA {DEPARTURE_DATE}: 최저 {cheapest["amount"]:,.0f} {cheapest["currency"]}'

    lines = [describe(i) for i in valid]
    text = header + "\n".join(lines)
    text += "\n\n※ 실제 결제 금액은 대한항공 홈페이지에서 꼭 다시 확인하세요."
    return subject, text


def send_email(subject, text):
    msg = MIMEText(text, _charset="utf-8")
    msg["Subject"] = subject
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = TO_EMAIL
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        smtp.send_message(msg)


if __name__ == "__main__":
    try:
        subject, text = build_message(search_fares())
    except Exception as e:
        subject, text = "항공권 가격 조회 실패", f"오류가 발생했어요:\n{e}"
    send_email(subject, text)
    print(subject)
