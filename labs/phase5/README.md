# Phase 5 – FastAPI 중급 (Day 81 ~ 100)

> **기간**: Day 81 – 100 | **총 160시간**

---

## 📋 Phase 5 학습 로드맵

| Day | 주제 | 핵심 키워드 |
|-----|------|------------|
| 81 | SQLite 기초 | SQL, DDL/DML, sqlite3 |
| 82 | SQLAlchemy Core | Engine, Connection, MetaData |
| 83 | SQLAlchemy ORM | `declarative_base`, `Session` |
| 84 | FastAPI + SQLAlchemy | CRUD, Session Depends |
| 85 | Alembic | `revision`, `upgrade`, `downgrade` |
| 86 | 패스워드 해싱 | `passlib`, bcrypt |
| 87 | JWT | `python-jose`, access/refresh token |
| 88 | OAuth2PasswordBearer | FastAPI 인증 흐름 |
| 89 | RBAC | Role 기반 접근 제어 |
| 90 | 페이지네이션 & 필터 | skip/limit, 쿼리 최적화 |
| 91 | 캐싱 | `functools.lru_cache`, Redis 기초 |
| 92 | 비동기 DB | `asyncpg`, `databases` |
| 93 | pytest + TestClient | API 단위 테스트 |
| 94 | pytest 고급 | DB fixture, 독립 테스트 DB |
| 95 | OpenAPI 문서화 심화 | tags, examples, description |
| 96 | 파일 업로드 | `UploadFile`, S3 기초 |
| 97 | 이메일 전송 | `fastapi-mail`, SMTP |
| 98 | 설정 관리 | `pydantic-settings`, `.env` |
| 99 | 미니 프로젝트 | JWT 인증 게시판 API |
| 100 | Phase 5 리뷰 | 코드 리뷰·자기평가 |

---

# Day 81 – SQLite 기초

## 📖 이론 (08:00 – 10:00)

```sql
-- SQL 기본
CREATE TABLE users (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT    NOT NULL,
    email   TEXT    UNIQUE NOT NULL,
    age     INTEGER,
    created_at TEXT DEFAULT (datetime('now'))
);

INSERT INTO users (name, email, age) VALUES ('홍길동','hong@test.com',25);
SELECT * FROM users WHERE age >= 20 ORDER BY name;
UPDATE users SET age = 26 WHERE id = 1;
DELETE FROM users WHERE id = 1;
```

## 🧪 LAB 실습 (10:00 – 17:00)

```python
# day81_sqlite.py
import sqlite3
from pathlib import Path

DB_PATH = Path("lab81.db")

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # dict-like 접근 허용
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db() -> None:
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT NOT NULL,
                email      TEXT UNIQUE NOT NULL,
                age        INTEGER,
                created_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS posts (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER REFERENCES users(id) ON DELETE CASCADE,
                title      TEXT NOT NULL,
                content    TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            );
        """)
    print("DB 초기화 완료")

def seed_data() -> None:
    users = [
        ("홍길동","hong@test.com",25),
        ("김철수","kim@test.com",30),
        ("이영희","lee@test.com",28),
    ]
    posts = [
        (1,"Python 기초","변수와 자료형"),
        (1,"FastAPI 시작","첫 번째 API"),
        (2,"SQLite 실습","DB 연동하기"),
    ]
    with get_connection() as conn:
        conn.executemany("INSERT OR IGNORE INTO users (name,email,age) VALUES (?,?,?)", users)
        conn.executemany("INSERT INTO posts (user_id,title,content) VALUES (?,?,?)", posts)

def get_users_with_posts() -> list[dict]:
    sql = """
        SELECT u.id, u.name, COUNT(p.id) as post_count
        FROM users u
        LEFT JOIN posts p ON p.user_id = u.id
        GROUP BY u.id
        ORDER BY post_count DESC
    """
    with get_connection() as conn:
        rows = conn.execute(sql).fetchall()
    return [dict(row) for row in rows]

init_db()
seed_data()
for row in get_users_with_posts():
    print(f"  {row['name']}: 게시글 {row['post_count']}개")
```

---

# Day 83-84 – SQLAlchemy ORM + FastAPI 연동

```python
# day84_fastapi_db.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
from typing import Generator

DATABASE_URL = "sqlite:///./lab84.db"
engine       = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base         = declarative_base()

# ORM 모델
class UserORM(Base):
    __tablename__ = "users"
    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(50), nullable=False)
    email      = Column(String(100), unique=True, nullable=False)
    age        = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)

Base.metadata.create_all(bind=engine)

# Pydantic 스키마
class UserCreate(BaseModel):
    name:  str
    email: str
    age:   int

class UserOut(UserCreate):
    id:         int
    created_at: datetime

    model_config = {"from_attributes": True}

# DB 세션 의존성
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="FastAPI + SQLAlchemy")

@app.post("/users", response_model=UserOut, status_code=201)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    if db.query(UserORM).filter(UserORM.email == data.email).first():
        raise HTTPException(409, "이미 존재하는 이메일")
    user = UserORM(**data.model_dump())
    db.add(user); db.commit(); db.refresh(user)
    return user

@app.get("/users", response_model=list[UserOut])
def list_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(UserORM).offset(skip).limit(limit).all()

@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(UserORM, user_id)
    if not user:
        raise HTTPException(404, f"유저 {user_id} 없음")
    return user

@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(UserORM, user_id)
    if not user:
        raise HTTPException(404, f"유저 {user_id} 없음")
    db.delete(user); db.commit()
```

---

# Day 87-88 – JWT 인증

```python
# day87_jwt.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM  = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES  = 30
REFRESH_TOKEN_EXPIRE_DAYS    = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

# 테스트
hashed = hash_password("my_password")
print(f"해시: {hashed}")
print(f"검증: {verify_password('my_password', hashed)}")

token = create_access_token({"sub": "user123", "role": "admin"})
print(f"토큰: {token[:50]}...")
payload = decode_token(token)
print(f"페이로드: {payload}")
```

```python
# day88_oauth2.py  – FastAPI 통합
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .day87_jwt import verify_password, create_access_token, decode_token, hash_password

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# 가짜 사용자 DB
fake_users_db = {
    "admin": {"username":"admin","hashed_password":hash_password("admin123"),"role":"admin"},
    "user1": {"username":"user1","hashed_password":hash_password("pass1"),   "role":"user"},
}

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보가 유효하지 않습니다",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        username = payload.get("sub")
        if not username or username not in fake_users_db:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    return fake_users_db[username]

@app.post("/auth/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form.username)
    if not user or not verify_password(form.password, user["hashed_password"]):
        raise HTTPException(401, "아이디 또는 비밀번호 오류")
    token = create_access_token({"sub": user["username"], "role": user["role"]})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {"username": current_user["username"], "role": current_user["role"]}

@app.get("/admin")
async def admin_only(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(403, "관리자만 접근 가능")
    return {"message": "관리자 전용 페이지"}
```

---

# Day 93-94 – FastAPI 테스트

```python
# day93_test_api.py
import pytest
from fastapi.testclient import TestClient
from day84_fastapi_db import app

client = TestClient(app)

def test_create_user():
    response = client.post("/users", json={"name":"테스트","email":"test@test.com","age":25})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "테스트"
    assert data["email"] == "test@test.com"
    assert "id" in data

def test_create_duplicate_email():
    client.post("/users", json={"name":"A","email":"dup@test.com","age":20})
    response = client.post("/users", json={"name":"B","email":"dup@test.com","age":21})
    assert response.status_code == 409

def test_get_user_not_found():
    response = client.get("/users/999999")
    assert response.status_code == 404

def test_list_users():
    response = client.get("/users?skip=0&limit=5")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_delete_user():
    # 생성
    r = client.post("/users", json={"name":"삭제용","email":"del@test.com","age":30})
    user_id = r.json()["id"]
    # 삭제
    r = client.delete(f"/users/{user_id}")
    assert r.status_code == 204
    # 재조회 → 404
    r = client.get(f"/users/{user_id}")
    assert r.status_code == 404
```

```python
# day94_test_advanced.py  – fixture + parametrize
import pytest
from fastapi.testclient import TestClient

@pytest.fixture(scope="session")
def test_app():
    """세션 범위 테스트 앱 (독립 테스트 DB)"""
    import os
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"  # 테스트 전용 DB
    from day84_fastapi_db import app, Base, engine
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)  # 테스트 후 정리

@pytest.fixture
def created_user(test_app):
    """테스트용 유저 자동 생성·삭제"""
    r = test_app.post("/users", json={"name":"픽스처","email":"fix@test.com","age":22})
    user = r.json()
    yield user
    test_app.delete(f"/users/{user['id']}")

@pytest.mark.parametrize("payload,expected_status", [
    ({"name":"유효","email":"valid@test.com","age":25},     201),
    ({"name":"X",   "email":"valid2@test.com","age":25},    422),   # 이름 너무 짧음
    ({"name":"유효2","email":"not-email","age":25},          422),   # 이메일 오류
])
def test_create_user_validation(test_app, payload, expected_status):
    r = test_app.post("/users", json=payload)
    assert r.status_code == expected_status
```

---

# Day 99 – 미니 프로젝트: JWT 인증 게시판 API

## 프로젝트 구조

```
board_api/
├── main.py
├── database.py         # SQLAlchemy 설정
├── models/
│   ├── user.py         # UserORM
│   └── post.py         # PostORM, CommentORM
├── schemas/
│   ├── user.py         # Pydantic 모델
│   └── post.py
├── routers/
│   ├── auth.py         # /auth/register, /auth/login, /auth/refresh
│   ├── users.py        # /users (인증 필요)
│   └── posts.py        # /posts CRUD
├── auth/
│   ├── jwt.py          # JWT 생성/검증
│   └── deps.py         # get_current_user Depends
└── tests/
    └── test_*.py
```

## API 스펙

| Method | Endpoint | 인증 | 설명 |
|--------|----------|------|------|
| POST | /auth/register | ✗ | 회원가입 |
| POST | /auth/login | ✗ | 로그인 → JWT |
| POST | /auth/refresh | ✓ | 토큰 갱신 |
| GET | /users/me | ✓ | 내 정보 |
| GET | /posts | ✗ | 전체 게시글 (페이지네이션) |
| POST | /posts | ✓ | 게시글 작성 |
| GET | /posts/{id} | ✗ | 게시글 상세 |
| PUT | /posts/{id} | ✓ (본인) | 수정 |
| DELETE | /posts/{id} | ✓ (본인/admin) | 삭제 |
| POST | /posts/{id}/comments | ✓ | 댓글 작성 |

---

# Day 100 – Phase 5 종합 리뷰

## 핵심 개념 다이어그램

```
HTTP 요청
    │
    ▼
FastAPI 라우터
    │
    ├─ Pydantic 입력 검증
    │
    ├─ Depends(get_current_user)  ← JWT 토큰 검증
    │       └─ Depends(get_db)    ← SQLAlchemy 세션
    │
    ├─ 비즈니스 로직
    │       └─ ORM CRUD
    │               └─ SQLite / PostgreSQL
    │
    ├─ Pydantic 응답 직렬화
    │
    └─ HTTP 응답
```

## 자기 평가

| 개념 | 자신감 (1-5) |
|------|-------------|
| SQLAlchemy ORM CRUD | /5 |
| Alembic 마이그레이션 | /5 |
| JWT 발급/검증 | /5 |
| OAuth2PasswordBearer | /5 |
| RBAC 권한 제어 | /5 |
| TestClient API 테스트 | /5 |
| pytest fixture/parametrize | /5 |
| pydantic-settings .env | /5 |
| **총점** | **/40** |

🔎 유튜브 관련 영상 검색: https://www.youtube.com/results?search_query=python+trading+README
