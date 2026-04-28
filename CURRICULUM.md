# 🐍 Python → FastAPI → Uvicorn 120일 LAB 커리큘럼

> **구성**: 하루 8시간 × 120일 = **960시간** 완성 로드맵  
> **스타일**: 매일 이론 강의(2h) + 실습 LAB(4h) + 과제 리뷰(2h)  
> **대상**: 프로그래밍 입문자 ~ 백엔드 주니어 개발자

---

## 📋 전체 Phase 구조

| Phase | 기간 | 주제 | 핵심 기술 |
|-------|------|------|-----------|
| **Phase 1** | Day 01 – 20 | Python 완전 기초 | 문법·자료형·제어문·함수 |
| **Phase 2** | Day 21 – 40 | 자료구조 & 객체지향(OOP) | list·dict·set·class·상속 |
| **Phase 3** | Day 41 – 60 | Python 고급 & 비동기 | 데코레이터·asyncio·타입힌트·Pydantic |
| **Phase 4** | Day 61 – 80 | FastAPI 기초 | 라우팅·요청/응답·미들웨어·Swagger |
| **Phase 5** | Day 81 – 100 | FastAPI 중급 | SQLite·SQLAlchemy·JWT·pytest |
| **Phase 6** | Day 101 – 120 | FastAPI 고급 & 실전 프로젝트 | WebSocket·Docker·배포·최종 프로젝트 |

---

## 📅 Phase 1 – Python 완전 기초 (Day 01 ~ 20)

| Day | 주제 | LAB 파일 |
|-----|------|----------|
| 01 | 개발환경 구축 – Python 설치, venv, VSCode, pip | `labs/phase1/day01_setup.md` |
| 02 | Hello World & 출력 함수 – print, f-string | `labs/phase1/day02_hello.md` |
| 03 | 변수와 자료형 – int, float, str, bool, None | `labs/phase1/day03_datatypes.md` |
| 04 | 연산자 – 산술·비교·논리·비트 연산 | `labs/phase1/day04_operators.md` |
| 05 | 문자열 심화 – 슬라이싱, 메서드, format | `labs/phase1/day05_strings.md` |
| 06 | 조건문 – if / elif / else, 삼항 연산자 | `labs/phase1/day06_conditions.md` |
| 07 | 반복문 – for, while, break, continue | `labs/phase1/day07_loops.md` |
| 08 | 함수 기초 – def, return, 매개변수 | `labs/phase1/day08_functions.md` |
| 09 | 함수 심화 – *args, **kwargs, 기본값, 스코프 | `labs/phase1/day09_advanced_functions.md` |
| 10 | 리스트 – 생성, CRUD, 정렬, 컴프리헨션 | `labs/phase1/day10_list.md` |
| 11 | 튜플과 언패킹 | `labs/phase1/day11_tuple.md` |
| 12 | 딕셔너리 – 생성, CRUD, 중첩, .get() | `labs/phase1/day12_dict.md` |
| 13 | 셋(Set) – 집합 연산, 중복 제거 | `labs/phase1/day13_set.md` |
| 14 | 파일 입출력 – open, read, write, with | `labs/phase1/day14_fileio.md` |
| 15 | JSON 처리 – json.dumps / json.loads / 파일 I/O | `labs/phase1/day15_json.md` |
| 16 | 예외처리 – try/except/finally, 사용자 예외 | `labs/phase1/day16_exceptions.md` |
| 17 | 모듈 & 패키지 – import, __init__.py, pip | `labs/phase1/day17_modules.md` |
| 18 | 표준 라이브러리 – os, sys, pathlib, datetime | `labs/phase1/day18_stdlib.md` |
| 19 | 미니 프로젝트 – JSON 기반 메모장 앱 | `labs/phase1/day19_project_memo.md` |
| 20 | Phase 1 종합 리뷰 & 코드 리뷰 세션 | `labs/phase1/day20_review.md` |

---

## 📅 Phase 2 – 자료구조 & 객체지향(OOP) (Day 21 ~ 40)

| Day | 주제 | LAB 파일 |
|-----|------|----------|
| 21 | 클래스 기초 – class, __init__, self | `labs/phase2/day21_class_basic.md` |
| 22 | 인스턴스 vs 클래스 속성·메서드 | `labs/phase2/day22_class_attr.md` |
| 23 | 상속 – 단일 상속, super() | `labs/phase2/day23_inheritance.md` |
| 24 | 다형성 & 메서드 오버라이딩 | `labs/phase2/day24_polymorphism.md` |
| 25 | 캡슐화 – private/protected, @property | `labs/phase2/day25_encapsulation.md` |
| 26 | 매직 메서드 – __str__, __repr__, __len__ | `labs/phase2/day26_magic_methods.md` |
| 27 | 추상 클래스 & 인터페이스 – abc 모듈 | `labs/phase2/day27_abstract.md` |
| 28 | 스택 & 큐 직접 구현 (list 기반) | `labs/phase2/day28_stack_queue.md` |
| 29 | 연결 리스트(Linked List) 구현 | `labs/phase2/day29_linked_list.md` |
| 30 | 이진 탐색 & 정렬 알고리즘 | `labs/phase2/day30_sorting.md` |
| 31 | 해시맵 심화 – dict 내부 원리, 충돌 | `labs/phase2/day31_hashmap.md` |
| 32 | 재귀함수 & 피보나치, 팩토리얼 | `labs/phase2/day32_recursion.md` |
| 33 | 컴프리헨션 심화 – list/dict/set/generator | `labs/phase2/day33_comprehension.md` |
| 34 | 이터레이터 & 이터러블 | `labs/phase2/day34_iterator.md` |
| 35 | 제너레이터 – yield, send, yield from | `labs/phase2/day35_generator.md` |
| 36 | 함수형 프로그래밍 – lambda, map, filter, reduce | `labs/phase2/day36_functional.md` |
| 37 | 정규표현식 – re 모듈 | `labs/phase2/day37_regex.md` |
| 38 | collections 모듈 – Counter, deque, defaultdict | `labs/phase2/day38_collections.md` |
| 39 | 미니 프로젝트 – OOP 기반 학생 성적 관리 시스템 | `labs/phase2/day39_project_grade.md` |
| 40 | Phase 2 종합 리뷰 & 코드 리뷰 세션 | `labs/phase2/day40_review.md` |

---

## 📅 Phase 3 – Python 고급 & 비동기 (Day 41 ~ 60)

| Day | 주제 | LAB 파일 |
|-----|------|----------|
| 41 | 데코레이터 기초 – @wrapper 패턴 | `labs/phase3/day41_decorator_basic.md` |
| 42 | 데코레이터 심화 – 인자 있는 데코레이터, @functools.wraps | `labs/phase3/day42_decorator_advanced.md` |
| 43 | 컨텍스트 매니저 – with, __enter__/__exit__ | `labs/phase3/day43_context_manager.md` |
| 44 | 타입 힌트 기초 – int, str, list, Optional, Union | `labs/phase3/day44_type_hints.md` |
| 45 | 타입 힌트 심화 – TypedDict, dataclass, Protocol | `labs/phase3/day45_advanced_types.md` |
| 46 | Pydantic v2 기초 – BaseModel, 유효성 검사 | `labs/phase3/day46_pydantic_basic.md` |
| 47 | Pydantic v2 심화 – validator, @field_validator, Config | `labs/phase3/day47_pydantic_advanced.md` |
| 48 | 동기 vs 비동기 – 블로킹/논블로킹 개념 | `labs/phase3/day48_sync_vs_async.md` |
| 49 | asyncio 기초 – async/await, event loop | `labs/phase3/day49_asyncio_basic.md` |
| 50 | asyncio 심화 – gather, Task, timeout | `labs/phase3/day50_asyncio_advanced.md` |
| 51 | HTTP 기초 – 요청/응답, 메서드, 상태코드 | `labs/phase3/day51_http_basics.md` |
| 52 | requests 라이브러리 – GET/POST/PUT/DELETE | `labs/phase3/day52_requests.md` |
| 53 | httpx – 비동기 HTTP 클라이언트 | `labs/phase3/day53_httpx.md` |
| 54 | 로깅 – logging 모듈, 레벨, 핸들러 | `labs/phase3/day54_logging.md` |
| 55 | 환경변수 & 설정관리 – dotenv, os.environ | `labs/phase3/day55_config.md` |
| 56 | 단위 테스트 기초 – unittest, pytest | `labs/phase3/day56_pytest_basic.md` |
| 57 | pytest 심화 – fixture, parametrize, mock | `labs/phase3/day57_pytest_advanced.md` |
| 58 | 파일 자동화 – PDF 생성 (fpdf), Excel (openpyxl) | `labs/phase3/day58_file_automation.md` |
| 59 | 미니 프로젝트 – 비동기 날씨 API 클라이언트 | `labs/phase3/day59_project_weather.md` |
| 60 | Phase 3 종합 리뷰 & 코드 리뷰 세션 | `labs/phase3/day60_review.md` |

---

## 📅 Phase 4 – FastAPI 기초 (Day 61 ~ 80)

| Day | 주제 | LAB 파일 |
|-----|------|----------|
| 61 | FastAPI 소개 & 설치 – uvicorn, Swagger UI | `labs/phase4/day61_fastapi_intro.md` |
| 62 | 첫 번째 API – GET /, 자동 문서화 | `labs/phase4/day62_first_api.md` |
| 63 | 경로 매개변수 – Path Parameter, 타입 변환 | `labs/phase4/day63_path_params.md` |
| 64 | 쿼리 매개변수 – Query Parameter, 기본값, Optional | `labs/phase4/day64_query_params.md` |
| 65 | 요청 본문 – Request Body, Pydantic 모델 | `labs/phase4/day65_request_body.md` |
| 66 | 응답 모델 – response_model, status_code | `labs/phase4/day66_response_model.md` |
| 67 | HTTP 메서드 – POST, PUT, PATCH, DELETE | `labs/phase4/day67_http_methods.md` |
| 68 | 폼 데이터 & 파일 업로드 | `labs/phase4/day68_form_file.md` |
| 69 | 헤더 & 쿠키 처리 | `labs/phase4/day69_header_cookie.md` |
| 70 | HTTPException & 에러 핸들러 | `labs/phase4/day70_exception.md` |
| 71 | 미들웨어 – CORS, GZip, 커스텀 미들웨어 | `labs/phase4/day71_middleware.md` |
| 72 | 의존성 주입 – Depends, 중첩 의존성 | `labs/phase4/day72_depends.md` |
| 73 | Router – APIRouter, 태그, prefix | `labs/phase4/day73_router.md` |
| 74 | 백그라운드 태스크 – BackgroundTasks | `labs/phase4/day74_background_tasks.md` |
| 75 | 정적 파일 & Jinja2 템플릿 | `labs/phase4/day75_static_template.md` |
| 76 | JSON 파일 기반 CRUD API (DB 없이) | `labs/phase4/day76_json_crud.md` |
| 77 | API 버전 관리 – prefix /v1, /v2 | `labs/phase4/day77_api_versioning.md` |
| 78 | Uvicorn 심화 – 설정, workers, SSL | `labs/phase4/day78_uvicorn_advanced.md` |
| 79 | 미니 프로젝트 – FastAPI 유저 관리 API | `labs/phase4/day79_project_users.md` |
| 80 | Phase 4 종합 리뷰 & 코드 리뷰 세션 | `labs/phase4/day80_review.md` |

---

## 📅 Phase 5 – FastAPI 중급 (Day 81 ~ 100)

| Day | 주제 | LAB 파일 |
|-----|------|----------|
| 81 | 관계형 DB 기초 – SQLite, SQL 기본 | `labs/phase5/day81_sqlite_basics.md` |
| 82 | SQLAlchemy Core – Engine, Connection, Table | `labs/phase5/day82_sqlalchemy_core.md` |
| 83 | SQLAlchemy ORM – declarative_base, 모델 정의 | `labs/phase5/day83_sqlalchemy_orm.md` |
| 84 | FastAPI + SQLAlchemy – Session, CRUD | `labs/phase5/day84_fastapi_db.md` |
| 85 | Alembic – 마이그레이션, revision, upgrade | `labs/phase5/day85_alembic.md` |
| 86 | 인증 기초 – 패스워드 해싱, passlib, bcrypt | `labs/phase5/day86_auth_password.md` |
| 87 | JWT 발급 & 검증 – python-jose, access/refresh token | `labs/phase5/day87_jwt.md` |
| 88 | OAuth2PasswordBearer – FastAPI 인증 흐름 | `labs/phase5/day88_oauth2.md` |
| 89 | Role 기반 접근 제어(RBAC) | `labs/phase5/day89_rbac.md` |
| 90 | 페이지네이션 & 필터링 – skip/limit, 쿼리 최적화 | `labs/phase5/day90_pagination.md` |
| 91 | 캐싱 – functools.lru_cache, Redis 기초 | `labs/phase5/day91_caching.md` |
| 92 | 비동기 DB – asyncpg, databases 라이브러리 | `labs/phase5/day92_async_db.md` |
| 93 | pytest + TestClient – FastAPI 테스트 | `labs/phase5/day93_testing_api.md` |
| 94 | pytest 고급 – DB fixture, 독립 테스트 DB | `labs/phase5/day94_testing_advanced.md` |
| 95 | API 문서화 심화 – OpenAPI tags, description, examples | `labs/phase5/day95_openapi_docs.md` |
| 96 | 파일 업로드 & S3 연동 기초 | `labs/phase5/day96_file_upload_s3.md` |
| 97 | 이메일 전송 – fastapi-mail, SMTP | `labs/phase5/day97_email.md` |
| 98 | 설정 관리 – pydantic-settings, .env | `labs/phase5/day98_settings.md` |
| 99 | 미니 프로젝트 – JWT 인증 포함 게시판 API | `labs/phase5/day99_project_board.md` |
| 100 | Phase 5 종합 리뷰 & 코드 리뷰 세션 | `labs/phase5/day100_review.md` |

---

## 📅 Phase 6 – FastAPI 고급 & 실전 프로젝트 (Day 101 ~ 120)

| Day | 주제 | LAB 파일 |
|-----|------|----------|
| 101 | WebSocket – 실시간 채팅 기초 | `labs/phase6/day101_websocket.md` |
| 102 | WebSocket 심화 – 룸, 브로드캐스트 | `labs/phase6/day102_websocket_rooms.md` |
| 103 | 비동기 작업 – Celery + Redis 기초 | `labs/phase6/day103_celery.md` |
| 104 | SSE (Server-Sent Events) – 실시간 알림 | `labs/phase6/day104_sse.md` |
| 105 | GraphQL 기초 – Strawberry + FastAPI | `labs/phase6/day105_graphql.md` |
| 106 | Docker 기초 – Dockerfile, 이미지, 컨테이너 | `labs/phase6/day106_docker_basic.md` |
| 107 | Docker Compose – FastAPI + DB 멀티 컨테이너 | `labs/phase6/day107_docker_compose.md` |
| 108 | CI/CD – GitHub Actions 파이프라인 | `labs/phase6/day108_cicd.md` |
| 109 | 클라우드 배포 – Railway / Render / Fly.io | `labs/phase6/day109_deploy_cloud.md` |
| 110 | 성능 최적화 – 프로파일링, N+1 문제, 인덱스 | `labs/phase6/day110_performance.md` |
| 111 | 보안 강화 – Rate Limiting, SQL Injection 방어 | `labs/phase6/day111_security.md` |
| 112 | 모니터링 – Prometheus, Grafana, Sentry | `labs/phase6/day112_monitoring.md` |
| 113 | 최종 프로젝트 설계 – 요구사항 정의, ERD, API 설계 | `labs/phase6/day113_project_design.md` |
| 114 | 최종 프로젝트 개발 1 – 모델 & 인증 구현 | `labs/phase6/day114_project_dev1.md` |
| 115 | 최종 프로젝트 개발 2 – 핵심 API 구현 | `labs/phase6/day115_project_dev2.md` |
| 116 | 최종 프로젝트 개발 3 – 파일 업로드·이메일 | `labs/phase6/day116_project_dev3.md` |
| 117 | 최종 프로젝트 개발 4 – 테스트 작성 | `labs/phase6/day117_project_dev4.md` |
| 118 | 최종 프로젝트 개발 5 – Docker & 배포 | `labs/phase6/day118_project_dev5.md` |
| 119 | 최종 프로젝트 발표 준비 & 코드 리뷰 | `labs/phase6/day119_project_review.md` |
| 120 | 최종 발표 & 수료식 | `labs/phase6/day120_graduation.md` |

---

## 🏗️ 일일 LAB 운영 방식

```
08:00 – 10:00  이론 강의    개념 설명 + 라이브 코딩 데모
10:00 – 12:00  LAB 실습 1  단계별 안내 실습 (guided)
12:00 – 13:00  점심 휴식
13:00 – 15:00  LAB 실습 2  자유 실습 + 심화 도전 과제
15:00 – 17:00  과제 작성    오늘 배운 내용으로 과제 완성
17:00 – 18:00  코드 리뷰    강사 피드백 + Q&A
```

---

## 📂 디렉터리 구조

```
labs/
├── phase1/   (Day 01–20) Python 완전 기초
├── phase2/   (Day 21–40) 자료구조 & OOP
├── phase3/   (Day 41–60) Python 고급 & 비동기
├── phase4/   (Day 61–80) FastAPI 기초
├── phase5/   (Day 81–100) FastAPI 중급
└── phase6/   (Day 101–120) FastAPI 고급 & 실전 프로젝트
```

---

## 🛠️ 공통 실습 환경

```bash
# Python 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# 핵심 패키지 설치
pip install fastapi uvicorn[standard] pydantic sqlalchemy alembic \
            python-jose passlib bcrypt httpx pytest pytest-asyncio \
            python-dotenv pydantic-settings fpdf2
```

---

## 📊 평가 기준

| 항목 | 비중 | 설명 |
|------|------|------|
| 일일 LAB 과제 | 40% | 매일 제출하는 실습 결과물 |
| Phase 미니 프로젝트 | 30% | Phase마다 진행하는 소규모 프로젝트 |
| 최종 프로젝트 | 30% | Day 113–120 개발·발표 |

---

*본 커리큘럼은 `edumgt/Python-FastAPI-Uvicorn` 레포지토리 기반으로 구성되었습니다.*
