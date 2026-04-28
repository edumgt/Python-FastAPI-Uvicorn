# Phase 3 – Python 고급 & 비동기 (Day 41 ~ 60)

> **기간**: Day 41 – 60 | **총 160시간**

---

## 📋 Phase 3 학습 로드맵

| Day | 주제 | 핵심 키워드 |
|-----|------|------------|
| 41 | 데코레이터 기초 | `@wrapper`, `functools.wraps` |
| 42 | 데코레이터 심화 | 인자 있는 데코레이터, 클래스 데코레이터 |
| 43 | 컨텍스트 매니저 | `with`, `__enter__/__exit__`, `contextlib` |
| 44 | 타입 힌트 기초 | `Optional`, `Union`, `list[T]`, `dict[K,V]` |
| 45 | 타입 힌트 심화 | `TypedDict`, `dataclass`, `Protocol`, `TypeVar` |
| 46 | Pydantic v2 기초 | `BaseModel`, 자동 유효성 검사 |
| 47 | Pydantic v2 심화 | `@field_validator`, `model_config`, `model_dump` |
| 48 | 동기 vs 비동기 | 블로킹/논블로킹, GIL, I/O 바운드 |
| 49 | asyncio 기초 | `async def`, `await`, `asyncio.run()` |
| 50 | asyncio 심화 | `gather`, `Task`, `timeout`, `Queue` |
| 51 | HTTP 기초 | 메서드, 상태코드, 헤더, JSON 응답 |
| 52 | requests 라이브러리 | `GET/POST/PUT/DELETE`, Session |
| 53 | httpx | 비동기 클라이언트, timeout, retry |
| 54 | 로깅 | `logging` 모듈, 레벨, 핸들러, 포매터 |
| 55 | 환경변수 & 설정 | `python-dotenv`, `os.environ` |
| 56 | pytest 기초 | `assert`, `pytest.raises`, 함수 테스트 |
| 57 | pytest 심화 | `fixture`, `parametrize`, `mock`, `patch` |
| 58 | 파일 자동화 | PDF(fpdf2), Excel(openpyxl) |
| 59 | 미니 프로젝트 | 비동기 날씨 API 클라이언트 |
| 60 | Phase 3 리뷰 | 코드 리뷰·자기평가 |

---

# Day 41 – 데코레이터 기초

## 🎯 학습 목표

- 데코레이터의 동작 원리 (함수를 감싸는 함수)
- `functools.wraps` 로 메타데이터 보존
- 실용 데코레이터 패턴: 타이머, 로거, 캐시

## 📖 이론 (08:00 – 10:00)

```python
import functools, time

# 데코레이터 기본 구조
def timer(func):
    @functools.wraps(func)    # 원본 함수 메타데이터 보존
    def wrapper(*args, **kwargs):
        start  = time.perf_counter()
        result = func(*args, **kwargs)
        end    = time.perf_counter()
        print(f"[{func.__name__}] {end - start:.6f}초 소요")
        return result
    return wrapper

def logger(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"▶ {func.__name__} 호출: args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"◀ {func.__name__} 반환: {result}")
        return result
    return wrapper

@timer
@logger
def slow_add(a: int, b: int) -> int:
    time.sleep(0.1)
    return a + b

result = slow_add(3, 5)
```

## 🧪 LAB 실습 (10:00 – 17:00)

```python
# day41_decorators.py
import functools, time, threading

# 1. 재시도 데코레이터
def retry(max_attempts: int = 3, delay: float = 0.5):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"  시도 {attempt}/{max_attempts}: {e}")
                    if attempt < max_attempts:
                        time.sleep(delay)
            raise RuntimeError(f"{func.__name__}: 모든 시도 실패")
        return wrapper
    return decorator

# 2. 캐싱 데코레이터 (functools.lru_cache 직접 구현)
def simple_cache(func):
    cache = {}
    @functools.wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    wrapper.cache = cache
    wrapper.cache_clear = lambda: cache.clear()
    return wrapper

@simple_cache
def fib(n: int) -> int:
    return n if n < 2 else fib(n-1) + fib(n-2)

print([fib(i) for i in range(10)])
print(f"캐시 크기: {len(fib.cache)}")

# 3. 타입 체크 데코레이터
def type_check(*types):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for arg, expected in zip(args, types):
                if not isinstance(arg, expected):
                    raise TypeError(f"예상: {expected.__name__}, 받음: {type(arg).__name__}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

@type_check(int, int)
def add(a: int, b: int) -> int:
    return a + b

print(add(3, 4))
try:
    add("3", 4)
except TypeError as e:
    print(f"타입 오류: {e}")
```

---

# Day 46 – Pydantic v2 기초

## 🎯 학습 목표

- `BaseModel`로 데이터 모델 정의
- 자동 타입 변환 및 유효성 검사
- `model_dump()`, `model_validate()` 활용
- FastAPI와의 연동 준비

## 📖 이론 (08:00 – 10:00)

```python
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class User(BaseModel):
    id:         int
    name:       str           = Field(..., min_length=2, max_length=50)
    email:      str           = Field(..., pattern=r'^[\w.-]+@[\w.-]+\.\w+$')
    age:        int           = Field(..., ge=0, le=150)
    is_active:  bool          = True
    created_at: datetime      = Field(default_factory=datetime.now)
    tags:       list[str]     = []
    score:      Optional[float] = None

# 유효성 검사 자동 수행
user = User(id=1, name="홍길동", email="hong@test.com", age=25)
print(user.model_dump())

# JSON 직렬화
import json
json_str = user.model_dump_json(indent=2)
print(json_str)

# JSON에서 역직렬화
user2 = User.model_validate_json(json_str)
print(user2 == user)

# 유효성 오류 테스트
from pydantic import ValidationError
try:
    bad_user = User(id=1, name="X", email="not-email", age=-5)
except ValidationError as e:
    print(e)
```

## 🧪 LAB 실습 (10:00 – 17:00)

```python
# day46_pydantic.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date
from enum import Enum

class Role(str, Enum):
    ADMIN  = "admin"
    USER   = "user"
    VIEWER = "viewer"

class Address(BaseModel):
    street: str
    city:   str
    country: str = "KR"

class UserCreate(BaseModel):
    username:  str  = Field(..., min_length=3, max_length=20)
    email:     str
    password:  str  = Field(..., min_length=8)
    role:      Role = Role.USER
    address:   Optional[Address] = None
    birth_date: Optional[date]   = None

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.replace("_","").isalnum():
            raise ValueError("영숫자와 _ 만 허용됩니다")
        return v.lower()

    @field_validator("email")
    @classmethod
    def email_format(cls, v: str) -> str:
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("유효하지 않은 이메일 형식")
        return v.lower()

# 테스트
from pydantic import ValidationError

valid = UserCreate(
    username="Hong_GilDong",
    email="Hong@Test.COM",
    password="securepassword",
    address=Address(street="광화문로 1", city="서울"),
    birth_date="1990-01-15",
)
print(valid.model_dump())

invalid_cases = [
    {"username":"ab","email":"x","password":"12345678"},   # 너무 짧은 username
    {"username":"홍길동","email":"hong@test.com","password":"12345678"},  # 한글 username
]
for case in invalid_cases:
    try:
        UserCreate(**case)
    except ValidationError as e:
        print(f"\n유효성 오류 ({case['username']}):")
        for err in e.errors():
            print(f"  [{err['loc'][0]}] {err['msg']}")
```

---

# Day 49 – asyncio 기초

## 🎯 학습 목표

- `async def` / `await` 코루틴 개념
- `asyncio.run()` 이벤트 루프 실행
- 동기 코드 vs 비동기 코드 성능 비교

## 📖 이론 (08:00 – 10:00)

```python
import asyncio
import time

# 동기 버전
def sync_fetch(url: str) -> str:
    time.sleep(1)    # 네트워크 I/O 시뮬레이션
    return f"데이터: {url}"

# 비동기 버전
async def async_fetch(url: str) -> str:
    await asyncio.sleep(1)    # 논블로킹 대기
    return f"데이터: {url}"

async def main():
    urls = [f"https://api.example.com/data/{i}" for i in range(5)]

    # 순차 실행 (5초)
    start = time.perf_counter()
    for url in urls:
        result = await async_fetch(url)
    print(f"순차: {time.perf_counter()-start:.2f}초")

    # 병렬 실행 (1초)
    start = time.perf_counter()
    results = await asyncio.gather(*[async_fetch(url) for url in urls])
    print(f"병렬: {time.perf_counter()-start:.2f}초")
    print(f"결과 수: {len(results)}")

asyncio.run(main())
```

## 🧪 LAB 실습 (10:00 – 17:00)

```python
# day49_asyncio.py
import asyncio
import random
import time

# 비동기 작업 시뮬레이션
async def process_order(order_id: int) -> dict:
    processing_time = random.uniform(0.5, 2.0)
    print(f"  주문 {order_id:3d} 처리 시작 (예상 {processing_time:.1f}초)")
    await asyncio.sleep(processing_time)
    return {"id": order_id, "status": "완료", "time": processing_time}

async def main():
    orders = list(range(1, 11))   # 주문 10개

    # 1. gather – 모두 동시 실행
    print("=== gather: 모두 동시 실행 ===")
    start = time.perf_counter()
    results = await asyncio.gather(*[process_order(i) for i in orders])
    elapsed = time.perf_counter() - start
    print(f"\n완료: {len(results)}건 | 총 소요: {elapsed:.2f}초")

    # 2. as_completed – 완료 순서대로 처리
    print("\n=== as_completed: 완료 순서대로 ===")
    start = time.perf_counter()
    tasks = [asyncio.create_task(process_order(i)) for i in orders[:5]]
    completed = 0
    for coro in asyncio.as_completed(tasks):
        result = await coro
        completed += 1
        print(f"  ✅ [{completed}/5] 주문 {result['id']} 완료")
    print(f"총 소요: {time.perf_counter()-start:.2f}초")

asyncio.run(main())
```

---

# Day 59 – 미니 프로젝트: 비동기 날씨 API 클라이언트

## 프로젝트 구조

```
weather_client/
├── __init__.py
├── models.py       # Pydantic WeatherData 모델
├── client.py       # httpx AsyncClient
├── cache.py        # 간단한 인메모리 캐시
└── main.py         # CLI 진입점
```

```python
# weather_client/models.py
from pydantic import BaseModel
from datetime import datetime

class WeatherData(BaseModel):
    city:        str
    temperature: float
    feels_like:  float
    humidity:    int
    description: str
    wind_speed:  float
    fetched_at:  datetime = None

class ForecastItem(BaseModel):
    date:        str
    temp_high:   float
    temp_low:    float
    description: str

class Forecast(BaseModel):
    city:  str
    items: list[ForecastItem]
```

```python
# weather_client/client.py  (Open-Meteo 무료 API 사용)
import httpx
import asyncio
from .models import WeatherData
from datetime import datetime

BASE_URL = "https://api.open-meteo.com/v1/forecast"
GEO_URL  = "https://geocoding-api.open-meteo.com/v1/search"

async def get_coordinates(city: str) -> tuple[float, float]:
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(GEO_URL, params={"name": city, "count": 1, "language": "ko"})
        r.raise_for_status()
        results = r.json().get("results", [])
        if not results:
            raise ValueError(f"도시를 찾을 수 없습니다: {city}")
        loc = results[0]
        return loc["latitude"], loc["longitude"]

async def get_weather(city: str) -> WeatherData:
    lat, lon = await get_coordinates(city)
    params = {
        "latitude": lat, "longitude": lon,
        "current_weather": True,
        "hourly": "relativehumidity_2m,apparent_temperature,windspeed_10m",
    }
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(BASE_URL, params=params)
        r.raise_for_status()
        data = r.json()
    cw = data["current_weather"]
    return WeatherData(
        city=city,
        temperature=cw["temperature"],
        feels_like=data["hourly"]["apparent_temperature"][0],
        humidity=data["hourly"]["relativehumidity_2m"][0],
        wind_speed=cw["windspeed"],
        description=f"날씨 코드: {cw['weathercode']}",
        fetched_at=datetime.now(),
    )

async def get_multi_weather(cities: list[str]) -> list[WeatherData]:
    tasks = [get_weather(city) for city in cities]
    return await asyncio.gather(*tasks, return_exceptions=True)
```

---

# Day 60 – Phase 3 종합 리뷰

## 핵심 개념 퀴즈

```python
# Q1. 아래 데코레이터의 실행 순서를 설명하세요
@decorator_a
@decorator_b
def my_func(): ...
# 답: decorator_b(my_func) 먼저 적용 → 결과를 decorator_a로 감싸기

# Q2. 아래 코드의 출력은?
async def f(): return 42
import asyncio
result = asyncio.run(f())
print(result, type(result))

# Q3. Pydantic vs dataclass 차이점을 3가지 말하세요

# Q4. asyncio.gather vs asyncio.wait 차이점은?

# Q5. httpx.AsyncClient 를 컨텍스트 매니저로 사용하는 이유는?
```

## 자기 평가

| 개념 | 자신감 (1-5) |
|------|-------------|
| 데코레이터 직접 구현 | /5 |
| Pydantic v2 유효성 검사 | /5 |
| async/await 흐름 이해 | /5 |
| asyncio.gather 병렬 실행 | /5 |
| httpx 비동기 클라이언트 | /5 |
| pytest fixture/mock | /5 |
| logging 설정 | /5 |
| 환경변수 관리 | /5 |
| **총점** | **/40** |
