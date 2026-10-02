"""flight_alert.py의 메시지 생성 함수를 샘플 응답으로 테스트"""
import unittest

# 환경변수 없이 모듈 함수만 임포트하기 위해 직접 로드
import importlib
import os
import sys

# 테스트용 더미 환경변수 세팅 (모듈 로드 시 필요)
os.environ.setdefault("IGNAV_API_KEY", "test-key")
os.environ.setdefault("GMAIL_ADDRESS", "test@gmail.com")
os.environ.setdefault("GMAIL_APP_PASSWORD", "test-password")

from flight_alert import build_message, describe


SAMPLE_ITINERARIES = [
    {
        "price": {"amount": 1_250_000, "currency": "KRW", "status": "verified"},
        "outbound": {
            "segments": [
                {
                    "marketing_carrier_code": "KE",
                    "flight_number": "17",
                    "departure_time_local": "2027-02-05T13:00:00",
                    "arrival_time_local": "2027-02-05T08:00:00",
                }
            ]
        },
    },
    {
        "price": {"amount": 1_480_000, "currency": "KRW", "status": "verified"},
        "outbound": {
            "segments": [
                {
                    "marketing_carrier_code": "KE",
                    "flight_number": "11",
                    "departure_time_local": "2027-02-05T09:30:00",
                    "arrival_time_local": "2027-02-05T04:30:00",
                }
            ]
        },
    },
    {
        "price": {"amount": 0, "currency": "KRW", "status": "placeholder"},
        "outbound": {
            "segments": [
                {
                    "marketing_carrier_code": "KE",
                    "flight_number": "1",
                    "departure_time_local": "2027-02-05T17:00:00",
                    "arrival_time_local": "2027-02-05T12:00:00",
                }
            ]
        },
    },
]


class TestBuildMessage(unittest.TestCase):
    def test_subject_contains_cheapest_price(self):
        subject, _ = build_message(SAMPLE_ITINERARIES)
        self.assertIn("1,250,000", subject)
        self.assertIn("KRW", subject)

    def test_body_excludes_zero_price(self):
        _, text = build_message(SAMPLE_ITINERARIES)
        self.assertNotIn("KE1 ", text)
        self.assertIn("KE17", text)
        self.assertIn("KE11", text)

    def test_sorted_by_price(self):
        _, text = build_message(SAMPLE_ITINERARIES)
        pos_17 = text.index("KE17")
        pos_11 = text.index("KE11")
        self.assertLess(pos_17, pos_11)

    def test_empty_itineraries(self):
        subject, text = build_message([])
        self.assertIn("조회 결과 없음", subject)
        self.assertIn("조회된 항공편이 없어요", text)

    def test_all_zero_prices(self):
        zeros = [SAMPLE_ITINERARIES[2]]
        subject, text = build_message(zeros)
        self.assertIn("조회 결과 없음", subject)

    def test_unverified_price_note(self):
        unverified = [
            {
                "price": {"amount": 900_000, "currency": "KRW", "status": "unverified"},
                "outbound": {
                    "segments": [
                        {
                            "marketing_carrier_code": "KE",
                            "flight_number": "17",
                            "departure_time_local": "2027-02-05T13:00:00",
                            "arrival_time_local": "2027-02-05T08:00:00",
                        }
                    ]
                },
            }
        ]
        _, text = build_message(unverified)
        self.assertIn("미확인 가격", text)


class TestDescribe(unittest.TestCase):
    def test_format(self):
        result = describe(SAMPLE_ITINERARIES[0])
        self.assertIn("KE17", result)
        self.assertIn("13:00 출발", result)
        self.assertIn("08:00 도착", result)
        self.assertIn("1,250,000", result)


if __name__ == "__main__":
    unittest.main()
