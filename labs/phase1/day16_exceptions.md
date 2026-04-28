# Day 16 – 예외처리

> **소요시간**: 8시간 | **Phase**: 1 – Python 완전 기초

---

## 🎯 학습 목표

- `try / except / else / finally` 구문 완전 이해
- 다중 예외 처리 및 예외 계층 구조
- 사용자 정의 예외 클래스 작성
- `raise`, `raise ... from ...` 활용

---

## 📖 이론 (08:00 – 10:00)

```python
# 기본 구조
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"오류: {e}")
else:
    print(f"성공: {result}")   # 예외 없을 때만
finally:
    print("항상 실행")          # 예외 유무 관계없이

# 다중 예외
def safe_parse(s: str) -> int:
    try:
        return int(s)
    except (ValueError, TypeError) as e:
        print(f"파싱 오류 ({type(e).__name__}): {e}")
        return 0

# 사용자 정의 예외
class AppError(Exception):
    """애플리케이션 기본 예외"""

class ValidationError(AppError):
    def __init__(self, field: str, message: str):
        self.field   = field
        self.message = message
        super().__init__(f"[{field}] {message}")

try:
    raise ValidationError("email", "올바른 이메일 형식이 아닙니다")
except ValidationError as e:
    print(f"유효성 오류 – 필드: {e.field}, 메시지: {e.message}")
```

---

## 🧪 LAB 1 – 예외 처리 패턴 (10:00 – 12:00)

```python
# day16_exceptions.py
import json
from pathlib import Path

# 1. 파일 읽기 안전 함수
def safe_read_json(path: str) -> dict | None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"파일 없음: {path}")
    except json.JSONDecodeError as e:
        print(f"JSON 파싱 오류: {e}")
    except PermissionError:
        print(f"권한 없음: {path}")
    return None

# 2. 안전한 나눗셈
def safe_divide(a: float, b: float) -> float:
    try:
        return a / b
    except ZeroDivisionError:
        raise ValueError(f"{a} / {b}: 0으로 나누기 불가") from None

# 3. 입력 검증 루프
def get_positive_int(prompt: str) -> int:
    while True:
        try:
            n = int(input(prompt))
            if n <= 0:
                raise ValueError("양수를 입력하세요")
            return n
        except ValueError as e:
            print(f"  ⚠️ {e}. 다시 입력하세요.")

# 테스트
safe_read_json("nonexistent.json")
safe_read_json("users.json")  # 이 repo에 있음
try:
    safe_divide(10, 0)
except ValueError as e:
    print(e)
```

---

## 🧪 LAB 2 – 사용자 정의 예외 계층 (13:00 – 15:00)

```python
# day16_custom_exceptions.py

class AppError(Exception):
    """앱 공통 예외"""

class AuthError(AppError):
    """인증 관련 예외"""
    def __init__(self, msg: str, user_id: str = ""):
        self.user_id = user_id
        super().__init__(msg)

class NotFoundError(AppError):
    """리소스 없음"""
    def __init__(self, resource: str, key):
        super().__init__(f"{resource} '{key}' 을(를) 찾을 수 없습니다")
        self.resource = resource
        self.key = key

class ValidationError(AppError):
    """유효성 검사 오류"""
    def __init__(self, field: str, msg: str):
        super().__init__(f"[{field}] {msg}")
        self.field = field

# 간단한 유저 서비스 시뮬레이션
users_db = {"alice": {"pw":"1234","role":"admin"}, "bob": {"pw":"5678","role":"user"}}

def login(user_id: str, pw: str) -> dict:
    if user_id not in users_db:
        raise NotFoundError("User", user_id)
    if users_db[user_id]["pw"] != pw:
        raise AuthError("비밀번호가 틀렸습니다", user_id)
    return users_db[user_id]

def create_user(user_id: str, pw: str) -> None:
    if len(user_id) < 3:
        raise ValidationError("user_id", "3글자 이상이어야 합니다")
    if len(pw) < 4:
        raise ValidationError("pw", "4글자 이상이어야 합니다")
    if user_id in users_db:
        raise ValidationError("user_id", "이미 존재하는 아이디입니다")

tests = [
    lambda: login("alice","1234"),
    lambda: login("unknown","pw"),
    lambda: login("bob","wrong"),
    lambda: create_user("ab","1234"),
    lambda: create_user("alice","5678"),
]
for test in tests:
    try:
        result = test()
        print(f"  성공: {result}")
    except (AuthError, NotFoundError, ValidationError) as e:
        print(f"  {type(e).__name__}: {e}")
```

---

## 🧪 LAB 3 – 예외를 활용한 재시도 패턴 (15:00 – 17:00)

```python
# day16_retry.py
import random
import time
from functools import wraps

def retry(max_attempts: int = 3, delay: float = 0.5, exceptions=(Exception,)):
    """재시도 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    print(f"  시도 {attempt}/{max_attempts} 실패: {e}")
                    if attempt < max_attempts:
                        time.sleep(delay)
            raise RuntimeError(f"{func.__name__}: {max_attempts}회 모두 실패")
        return wrapper
    return decorator

@retry(max_attempts=3, delay=0.1, exceptions=(ConnectionError,))
def unstable_api_call(endpoint: str) -> dict:
    """랜덤하게 실패하는 API 호출 시뮬레이션"""
    if random.random() < 0.6:  # 60% 확률로 실패
        raise ConnectionError(f"연결 실패: {endpoint}")
    return {"status": "ok", "endpoint": endpoint}

try:
    result = unstable_api_call("/api/data")
    print(f"\n성공: {result}")
except RuntimeError as e:
    print(f"\n최종 실패: {e}")
```

---

## 📝 과제 (17:00 – 18:00)

`day16_homework.py` – 파일 안전 처리기

1. `SafeFileProcessor` 클래스 구현
2. `read(path)`: 없으면 `FileNotFoundError`, 빈 파일이면 `ValueError`
3. `write(path, content)`: 쓰기 권한 없으면 커스텀 `WriteError`
4. `backup(path)`: 파일을 `path.bak`으로 복사, 실패 시 원본 유지
5. 각 메서드에 `try/except/finally` 적용

---

## ✅ 체크리스트

- [ ] `try/except/else/finally` 모두 사용
- [ ] 다중 예외 처리 (`except (A, B)`)
- [ ] 사용자 정의 예외 계층 구조 구현
- [ ] `raise ... from None` 사용
- [ ] 재시도 데코레이터 완성
- [ ] SafeFileProcessor 과제 완성
