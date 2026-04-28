# 🐍 Python → FastAPI → Uvicorn 학습 프로젝트

> **Python 기초부터 FastAPI 백엔드, 금융 데이터 분석까지** — 총 150일(1,200시간) 커리큘럼 기반 학습 저장소입니다.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-latest-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Uvicorn](https://img.shields.io/badge/Uvicorn-ASGI-4c4c4c)](https://www.uvicorn.org/)

---

## 📌 프로젝트 소개

이 저장소는 **Python 입문자부터 백엔드 주니어 개발자**를 목표 대상으로 하는 단계별 실습 프로젝트입니다.  
루트 디렉터리에는 초기 실습 예제 파일들이, `labs/` 디렉터리에는 Phase별 LAB 자료가 포함되어 있습니다.

| 항목 | 내용 |
|------|------|
| 대상 | Python 입문자 ~ 백엔드 주니어 개발자 / 금융 데이터 분석 입문자 |
| 구성 | 하루 8시간 × 150일 = **1,200시간** |
| 운영 | 이론 강의(2h) + 실습 LAB(4h) + 과제 리뷰(2h) |

---

## 📋 Phase 구조 개요

| Phase | 기간 | 주제 |
|-------|------|------|
| Phase 1 | Day 01 – 20 | Python 완전 기초 (문법·자료형·함수·파일 I/O) |
| Phase 2 | Day 21 – 40 | 자료구조 & 객체지향(OOP) |
| Phase 3 | Day 41 – 60 | Python 고급 & 비동기 (asyncio·Pydantic·pytest) |
| Phase 4 | Day 61 – 80 | FastAPI 기초 (라우팅·요청/응답·Swagger) |
| Phase 5 | Day 81 – 100 | FastAPI 중급 (SQLAlchemy·JWT·캐싱·테스트) |
| Phase 6 | Day 101 – 120 | FastAPI 고급 & 실전 프로젝트 (Docker·배포·CI/CD) |
| Phase 7 | Day 121 – 150 | 금융 데이터 분석 & 머신러닝 (yfinance·pandas·LSTM) |

> 📄 전체 일일 커리큘럼은 **[CURRICULUM.md](./CURRICULUM.md)** 를 참고하세요.

---

## 📂 디렉터리 구조

```
Python-FastAPI-Uvicorn/
├── app.py              # FastAPI 앱 (GET /, /user, /fruits)
├── mydata.py           # dict 데이터 예제
├── arraylist.py        # 리스트 자료구조 실습
├── hashmap.py          # 해시맵(dict) 실습
├── hashtest.py         # set 집합 연산 실습
├── logintest.py        # JSON 파일 기반 로그인 시뮬레이션
├── pdftest.py          # FPDF를 이용한 PDF 자동 생성 (한글 지원)
├── hwptest.py          # pywin32를 이용한 HWP COM 자동화 (Windows 전용)
├── users.json          # 사용자 데이터 (로그인 실습용)
├── loginusers.json     # 로그인 상태 저장 파일
├── requirements.txt    # 패키지 의존성
├── CURRICULUM.md       # 150일 전체 커리큘럼
└── labs/
    ├── phase1/   (Day 01–20)  Python 완전 기초
    ├── phase2/   (Day 21–40)  자료구조 & OOP
    ├── phase3/   (Day 41–60)  Python 고급 & 비동기
    ├── phase4/   (Day 61–80)  FastAPI 기초
    ├── phase5/   (Day 81–100) FastAPI 중급
    ├── phase6/   (Day 101–120) FastAPI 고급 & 실전 프로젝트
    └── phase7/   (Day 121–150) 금융 데이터 분석 & 머신러닝
```

---

## 🚀 빠른 시작

### 1. 가상환경 생성 및 활성화

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 2. 패키지 설치

```bash
pip install fastapi uvicorn
# 또는 저장된 의존성 일괄 설치
pip install -r requirements.txt
```

### 3. FastAPI 서버 실행

```bash
uvicorn app:app --reload
```

서버 실행 후 브라우저에서 확인:

| URL | 설명 |
|-----|------|
| `http://127.0.0.1:8000/` | Hello 메시지 반환 |
| `http://127.0.0.1:8000/user` | mydata.py dict 데이터 반환 |
| `http://127.0.0.1:8000/fruits` | hashtest.py set 처리 결과 반환 |
| `http://127.0.0.1:8000/docs` | Swagger UI 자동 문서 |

---

## 🛠️ 기술 스택

| 구분 | 기술 |
|------|------|
| 언어 | Python 3.10+ |
| 웹 프레임워크 | FastAPI |
| ASGI 서버 | Uvicorn |
| 데이터 저장 | JSON 파일 (DB 없이 학습 목적) |
| 문서 자동화 | FPDF (PDF 생성), pywin32 (HWP, Windows 전용) |
| 금융/ML (Phase 7) | yfinance, pandas, scikit-learn, TensorFlow/Keras |

---

## 📦 의존성 관리

```bash
# 현재 설치된 패키지 확인
pip list

# requirements.txt 갱신
pip freeze > requirements.txt
```

---

## 📊 평가 기준 (수강생 대상)

| 항목 | 비중 | 설명 |
|------|------|------|
| 일일 LAB 과제 | 40% | 매일 제출하는 실습 결과물 |
| Phase 미니 프로젝트 | 30% | Phase마다 진행하는 소규모 프로젝트 |
| 최종 프로젝트 | 30% | FastAPI 실전 프로젝트 또는 금융 ML 프로젝트 |

---

*본 저장소는 `edumgt/Python-FastAPI-Uvicorn` 기반 교육 커리큘럼을 위해 구성되었습니다.*
