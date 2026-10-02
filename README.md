# 대한항공 항공권 가격 알림

매일 아침(한국시간 08:00) 대한항공 인천(ICN) → LA(LAX) 직항 최저가를 조회해서 Gmail로 알려주는 자동화입니다.

## 구조

```
flight_alert.py              # 가격 조회 + 이메일 발송
test_flight_alert.py         # 메시지 생성 테스트
.github/workflows/daily.yml  # GitHub Actions 스케줄
```

## 세팅 순서

### 1. Ignav API 키 발급

1. [ignav.com](https://ignav.com) 가입
2. Dashboard → API Keys에서 키 생성
3. 생성된 키를 복사해 둡니다

### 2. Gmail 앱 비밀번호 발급

1. [Google 계정 보안](https://myaccount.google.com/security) 접속
2. **2단계 인증**이 켜져 있는지 확인 (꺼져 있으면 먼저 켜세요)
3. 검색창에 "앱 비밀번호" 검색 → **앱 비밀번호** 클릭
4. 앱 이름에 `flight-alert` 입력 후 생성
5. 나오는 16자리 비밀번호를 복사해 둡니다 (공백 제거)

### 3. GitHub Secrets 등록

이 저장소의 **Settings → Secrets and variables → Actions → New repository secret**에서 아래 4개를 등록합니다:

| Secret 이름 | 값 |
|---|---|
| `IGNAV_API_KEY` | Ignav에서 발급받은 API 키 |
| `GMAIL_ADDRESS` | 보내는 Gmail 주소 (예: `me@gmail.com`) |
| `GMAIL_APP_PASSWORD` | 위에서 발급받은 16자리 앱 비밀번호 |
| `TO_EMAIL` | 받을 이메일 주소 (생략하면 `GMAIL_ADDRESS`로 발송) |

### 4. 수동 실행 테스트

1. 저장소의 **Actions** 탭 → **Daily flight price** 워크플로우 클릭
2. **Run workflow** 버튼을 눌러 수동 실행
3. 이메일이 오는지 확인

### 5. (선택) 조회 조건 변경

`flight_alert.py` 상단의 상수를 수정하면 됩니다:

```python
ORIGIN = "ICN"
DESTINATION = "LAX"
DEPARTURE_DATE = "2027-02-05"
AIRLINE = "KE"
NONSTOP_ONLY = True
```

## gh CLI로 Secrets 등록하기

```bash
gh secret set IGNAV_API_KEY --body "여기에_API_키"
gh secret set GMAIL_ADDRESS --body "me@gmail.com"
gh secret set GMAIL_APP_PASSWORD --body "xxxx xxxx xxxx xxxx"
gh secret set TO_EMAIL --body "받을주소@gmail.com"
```

## 로컬 테스트

```bash
python -m pytest test_flight_alert.py -v
# 또는
python -m unittest test_flight_alert.py -v
```

## 체크리스트 (직접 해야 할 것)

- [ ] Ignav 가입 및 API 키 발급
- [ ] Gmail 2단계 인증 켜기 + 앱 비밀번호 발급
- [ ] GitHub Secrets 4개 등록 (`IGNAV_API_KEY`, `GMAIL_ADDRESS`, `GMAIL_APP_PASSWORD`, `TO_EMAIL`)
- [ ] Actions 탭에서 수동 실행 → 이메일 수신 확인
