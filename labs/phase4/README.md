# Phase 4 – FastAPI 기초 (Day 61 ~ 80)

> **기간**: Day 61 – 80 | **총 160시간**

---

## 📋 Phase 4 학습 로드맵

| Day | 주제 | 핵심 키워드 |
|-----|------|------------|
| 61 | FastAPI 소개 & 설치 | `FastAPI()`, `uvicorn`, Swagger UI |
| 62 | 첫 번째 API | `@app.get`, 자동 문서화 |
| 63 | 경로 매개변수 | `{param}`, 타입 변환, `Path()` |
| 64 | 쿼리 매개변수 | `Query()`, 기본값, `Optional` |
| 65 | 요청 본문 | `BaseModel`, `Body()` |
| 66 | 응답 모델 | `response_model`, `JSONResponse` |
| 67 | HTTP 메서드 | POST/PUT/PATCH/DELETE 완전 CRUD |
| 68 | 폼 & 파일 | `Form()`, `UploadFile` |
| 69 | 헤더 & 쿠키 | `Header()`, `Cookie()` |
| 70 | 예외 처리 | `HTTPException`, 커스텀 핸들러 |
| 71 | 미들웨어 | CORS, GZip, 커스텀 미들웨어 |
| 72 | 의존성 주입 | `Depends()`, 중첩 의존성 |
| 73 | Router | `APIRouter`, prefix, tags |
| 74 | 백그라운드 태스크 | `BackgroundTasks` |
| 75 | 정적 파일 & 템플릿 | `StaticFiles`, Jinja2 |
| 76 | JSON CRUD API | 파일 기반 (이 repo 패턴 확장) |
| 77 | API 버전 관리 | prefix v1/v2 |
| 78 | Uvicorn 심화 | workers, reload, SSL |
| 79 | 미니 프로젝트 | 유저 관리 API |
| 80 | Phase 4 리뷰 | 코드 리뷰·자기평가 |

---

# Day 61 – FastAPI 소개 & 설치

## 🎯 학습 목표

- FastAPI 특징 이해 (자동 문서화, Pydantic, 비동기)
- Uvicorn ASGI 서버 개념
- 기존 app.py 코드 분석
- Swagger UI / ReDoc 사용법

## 📖 이론 (08:00 – 10:00)

### FastAPI의 4가지 강점

1. **자동 문서화**: OpenAPI(Swagger UI, ReDoc) 자동 생성
2. **타입 안전성**: Pydantic v2 기반 요청/응답 검증
3. **비동기 지원**: `async def` 기반 고성능
4. **빠른 개발**: 최소한의 코드로 API 구성

### ASGI vs WSGI

```
WSGI (Flask/Django): 동기 → 한 번에 1 요청
ASGI (FastAPI):      비동기 → 동시에 여러 요청 처리
```

## 🧪 LAB 1 – 설치 및 첫 실행 (10:00 – 12:00)

```bash
# 설치
pip install fastapi uvicorn[standard] pydantic

# 버전 확인
python -c "import fastapi; print(fastapi.__version__)"
```

```python
# day61_hello_fastapi.py
from fastapi import FastAPI
from datetime import datetime

app = FastAPI(
    title="Phase 4 LAB API",
    description="Python-FastAPI-Uvicorn 커리큘럼 실습",
    version="0.1.0",
)

@app.get("/")
async def root():
    return {"message": "Hello, FastAPI!", "time": datetime.now().isoformat()}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": app.version}

@app.get("/info")
async def info():
    return {
        "framework": "FastAPI",
        "server":    "Uvicorn",
        "docs":      "/docs",
        "redoc":     "/redoc",
    }
```

```bash
# 실행
uvicorn day61_hello_fastapi:app --reload --port 8000

# 브라우저에서 확인
# http://localhost:8000/docs   ← Swagger UI
# http://localhost:8000/redoc  ← ReDoc
```

## 🧪 LAB 2 – 이 repo의 app.py 분석 & 확장 (13:00 – 15:00)

```python
# day61_app_extended.py  (이 repo의 app.py 기반 확장)
from fastapi import FastAPI
from mydata   import get_data
from hashtest import get_fruits_info
from datetime import datetime
import platform

app = FastAPI(title="Python-FastAPI-Uvicorn Extended")

# 기존 엔드포인트 (이 repo에서 그대로 가져옴)
@app.get("/")
async def root():
    return {"message": "Hello, FastAPI!"}

@app.get("/user")
async def user_info():
    return get_data()

@app.get("/fruits")
async def fruits_info():
    return get_fruits_info()

# 새로 추가하는 엔드포인트들
@app.get("/system")
async def system_info():
    return {
        "os":       platform.system(),
        "python":   platform.python_version(),
        "time":     datetime.now().isoformat(),
    }

@app.get("/echo/{message}")
async def echo(message: str):
    return {"echo": message, "length": len(message)}
```

---

# Day 62-65 – 경로/쿼리/요청본문

## Day 62 – 첫 번째 API

```python
# day62_first_api.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# 정적 라우트
@app.get("/")
async def root(): return {"msg": "root"}

@app.get("/about")
async def about(): return {"title": "FastAPI 실습", "author": "수강생"}

# 응답에 타입 명시
class GreetingResponse(BaseModel):
    greeting:  str
    timestamp: str

from datetime import datetime

@app.get("/greet/{name}", response_model=GreetingResponse)
async def greet(name: str) -> GreetingResponse:
    return GreetingResponse(
        greeting  = f"안녕하세요, {name}님!",
        timestamp = datetime.now().isoformat(),
    )
```

## Day 63 – 경로 매개변수

```python
# day63_path_params.py
from fastapi import FastAPI, Path, HTTPException
from enum import Enum

app = FastAPI()

class ItemCategory(str, Enum):
    electronics = "electronics"
    clothing    = "clothing"
    food        = "food"

# 정수 경로 변수 + 유효성
@app.get("/items/{item_id}")
async def get_item(
    item_id: int = Path(..., ge=1, le=9999, description="상품 ID (1-9999)")
):
    return {"item_id": item_id, "name": f"상품{item_id}"}

# 열거형 경로 변수
@app.get("/categories/{category}")
async def get_category(category: ItemCategory):
    descriptions = {
        ItemCategory.electronics: "전자제품 카테고리",
        ItemCategory.clothing:    "의류 카테고리",
        ItemCategory.food:        "식품 카테고리",
    }
    return {"category": category.value, "desc": descriptions[category]}

# 경로 변수 + 추가 경로 캡처
@app.get("/files/{file_path:path}")
async def get_file(file_path: str):
    return {"path": file_path}
```

## Day 64 – 쿼리 매개변수

```python
# day64_query_params.py
from fastapi import FastAPI, Query
from typing import Optional

app = FastAPI()

ITEMS = [
    {"id":1,"name":"노트북","category":"electronics","price":1500000},
    {"id":2,"name":"마우스","category":"electronics","price":35000},
    {"id":3,"name":"티셔츠","category":"clothing","price":25000},
    {"id":4,"name":"청바지","category":"clothing","price":79000},
    {"id":5,"name":"사과","category":"food","price":5000},
]

@app.get("/items")
async def list_items(
    category:  Optional[str] = Query(None, description="카테고리 필터"),
    min_price: Optional[int] = Query(None, ge=0, description="최소 가격"),
    max_price: Optional[int] = Query(None, ge=0, description="최대 가격"),
    q:         Optional[str] = Query(None, min_length=1, description="이름 검색"),
    skip:      int           = Query(0, ge=0, description="건너뛸 수"),
    limit:     int           = Query(10, ge=1, le=100, description="최대 반환 수"),
    sort_by:   str           = Query("id", description="정렬 기준: id/name/price"),
    desc:      bool          = Query(False, description="내림차순 정렬"),
):
    result = ITEMS.copy()
    if category:
        result = [i for i in result if i["category"] == category]
    if min_price is not None:
        result = [i for i in result if i["price"] >= min_price]
    if max_price is not None:
        result = [i for i in result if i["price"] <= max_price]
    if q:
        result = [i for i in result if q.lower() in i["name"].lower()]
    result.sort(key=lambda i: i.get(sort_by, i["id"]), reverse=desc)
    return {"total": len(result), "items": result[skip:skip+limit]}
```

## Day 65 – 요청 본문

```python
# day65_request_body.py
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

app = FastAPI()

class ItemCreate(BaseModel):
    name:        str   = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price:       float = Field(..., gt=0)
    stock:       int   = Field(..., ge=0)
    category:    str

class ItemResponse(ItemCreate):
    id:         int
    created_at: str

items_db: list[ItemResponse] = []
next_id  = 1

@app.post("/items", response_model=ItemResponse, status_code=201)
async def create_item(item: ItemCreate):
    global next_id
    new_item = ItemResponse(
        **item.model_dump(),
        id=next_id,
        created_at=datetime.now().isoformat(),
    )
    items_db.append(new_item)
    next_id += 1
    return new_item

@app.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    from fastapi import HTTPException
    item = next((i for i in items_db if i.id == item_id), None)
    if not item:
        raise HTTPException(404, f"상품 {item_id} 없음")
    return item
```

---

# Day 67 – 완전한 CRUD API

```python
# day67_crud.py
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

app = FastAPI(title="완전한 CRUD API")

class UserCreate(BaseModel):
    name:  str  = Field(..., min_length=2)
    email: str
    age:   int  = Field(..., ge=0, le=150)

class UserUpdate(BaseModel):
    name:  Optional[str]  = Field(None, min_length=2)
    email: Optional[str]  = None
    age:   Optional[int]  = Field(None, ge=0, le=150)

class UserResponse(BaseModel):
    id:         int
    name:       str
    email:      str
    age:        int
    created_at: str
    updated_at: str

db:      dict[int, UserResponse] = {}
next_id: int = 1

@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreate):
    global next_id
    now  = datetime.now().isoformat(timespec="seconds")
    user = UserResponse(**data.model_dump(), id=next_id, created_at=now, updated_at=now)
    db[next_id] = user
    next_id += 1
    return user

@app.get("/users", response_model=list[UserResponse])
async def list_users():
    return list(db.values())

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    if user_id not in db:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"유저 {user_id} 없음")
    return db[user_id]

@app.put("/users/{user_id}", response_model=UserResponse)
async def replace_user(user_id: int, data: UserCreate):
    if user_id not in db:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"유저 {user_id} 없음")
    updated = UserResponse(
        **data.model_dump(), id=user_id,
        created_at=db[user_id].created_at,
        updated_at=datetime.now().isoformat(timespec="seconds"),
    )
    db[user_id] = updated
    return updated

@app.patch("/users/{user_id}", response_model=UserResponse)
async def partial_update(user_id: int, data: UserUpdate):
    if user_id not in db:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"유저 {user_id} 없음")
    old   = db[user_id].model_dump()
    patch = {k: v for k, v in data.model_dump().items() if v is not None}
    old.update(patch)
    old["updated_at"] = datetime.now().isoformat(timespec="seconds")
    db[user_id] = UserResponse(**old)
    return db[user_id]

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    if user_id not in db:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"유저 {user_id} 없음")
    del db[user_id]
```

---

# Day 72 – 의존성 주입 (Depends)

```python
# day72_depends.py
from fastapi import FastAPI, Depends, HTTPException, Header
from typing import Annotated

app = FastAPI()

# 공통 페이지네이션 의존성
def pagination(skip: int = 0, limit: int = 10) -> dict:
    return {"skip": skip, "limit": limit}

# 인증 의존성
async def verify_token(x_token: Annotated[str, Header()]) -> str:
    if x_token != "secret-token":
        raise HTTPException(401, "유효하지 않은 토큰")
    return x_token

# 데이터베이스 세션 의존성 (DB 없이 시뮬레이션)
class FakeDB:
    def __init__(self): self.connected = True
    def close(self):    self.connected = False

def get_db():
    db = FakeDB()
    try:
        yield db
    finally:
        db.close()

ITEMS = list(range(1, 101))

@app.get("/items")
async def list_items(
    page: Annotated[dict, Depends(pagination)],
    db:   Annotated[FakeDB, Depends(get_db)],
    token: Annotated[str, Depends(verify_token)],
):
    start = page["skip"]
    end   = start + page["limit"]
    return {
        "db_connected": db.connected,
        "items":  ITEMS[start:end],
        "total":  len(ITEMS),
    }
```

---

# Day 79 – 미니 프로젝트: 유저 관리 API

## 프로젝트 구조

```
user_api/
├── __init__.py
├── main.py          # FastAPI app 생성
├── routers/
│   ├── __init__.py
│   ├── users.py     # /users CRUD
│   └── auth.py      # /auth/login, /auth/logout
├── models/
│   ├── __init__.py
│   └── user.py      # Pydantic 모델
├── storage/
│   ├── __init__.py
│   └── json_store.py  # JSON 파일 저장소
└── dependencies.py  # 공통 Depends
```

```python
# user_api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import users, auth

app = FastAPI(
    title="유저 관리 API",
    description="Phase 4 최종 미니 프로젝트",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,  prefix="/auth",  tags=["인증"])
app.include_router(users.router, prefix="/users", tags=["유저"])

@app.get("/", tags=["root"])
async def root():
    return {"message": "유저 관리 API", "docs": "/docs"}
```

## API 스펙

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | /auth/login | 로그인 (JSON 파일 기반) |
| POST | /auth/logout | 로그아웃 |
| GET | /users | 전체 유저 목록 (페이지네이션) |
| POST | /users | 유저 등록 |
| GET | /users/{id} | 특정 유저 조회 |
| PUT | /users/{id} | 유저 정보 전체 수정 |
| PATCH | /users/{id} | 유저 정보 부분 수정 |
| DELETE | /users/{id} | 유저 삭제 |
| GET | /users/search | 이름/이메일 검색 |

---

# Day 80 – Phase 4 종합 리뷰

## FastAPI 핵심 개념 퀴즈

```python
# Q1. 경로 매개변수와 쿼리 매개변수의 차이점은?
# GET /items/5        → item_id=5 는 경로 매개변수
# GET /items?id=5     → id=5 는 쿼리 매개변수

# Q2. status_code=201 과 204의 차이는?
# 201 Created: 생성 성공, 응답 본문 있음
# 204 No Content: 처리 성공, 응답 본문 없음

# Q3. Depends()를 사용하는 이유 3가지는?
# 1. 코드 재사용 (공통 로직 분리)
# 2. 의존성 명확화 (테스트 용이)
# 3. 자동 문서화 (Swagger에 표시)

# Q4. response_model의 역할은?
# 1. 응답 데이터 필터링 (불필요 필드 제거)
# 2. Swagger 문서에 응답 스키마 자동 생성
# 3. 직렬화 전 유효성 검사

# Q5. CORS 미들웨어가 필요한 이유는?
# 브라우저의 Same-Origin Policy 우회
# 다른 도메인(예: React 앱)에서 API 호출 허용
```

## 자기 평가

| 개념 | 자신감 (1-5) |
|------|-------------|
| FastAPI 앱 생성 & 설정 | /5 |
| 경로/쿼리 매개변수 | /5 |
| Pydantic 요청/응답 모델 | /5 |
| CRUD (POST/GET/PUT/PATCH/DELETE) | /5 |
| HTTPException 처리 | /5 |
| Depends 의존성 주입 | /5 |
| APIRouter 분리 | /5 |
| CORS 미들웨어 | /5 |
| **총점** | **/40** |

🔎 유튜브 관련 영상 검색: https://www.youtube.com/results?search_query=python+trading+README
