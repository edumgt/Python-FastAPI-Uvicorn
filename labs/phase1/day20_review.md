# Day 20 – Phase 1 종합 리뷰 & 코드 리뷰 세션

> **소요시간**: 8시간 | **Phase**: 1 – Python 완전 기초

---

## 🎯 오늘의 목표

- Day 01–19 핵심 개념 총복습
- 개인 코드 리뷰 및 리팩터링 실습
- 자기 평가 테스트 (모의 퀴즈)
- Phase 2 예고

---

## 📖 Phase 1 핵심 개념 요약 (08:00 – 10:00)

### 자료형 & 연산자

```python
# 기본 자료형 6가지
n, f, s, b, none, c = 42, 3.14, "Python", True, None, 2+3j

# 중요 연산자
17 // 5   # 3  (정수 나눗셈)
17 % 5    # 2  (나머지)
2 ** 10   # 1024 (거듭제곱)
```

### 컨테이너 선택 기준

| 상황 | 선택 |
|------|------|
| 순서 있음, 변경 필요 | `list` |
| 순서 있음, 불변 | `tuple` |
| 키-값 매핑 | `dict` |
| 고유값, 집합 연산 | `set` |

### 함수 시그니처 체계

```python
def func(pos_only, /, normal, *, kw_only, **kwargs) -> return_type:
    ...
```

### 예외 계층

```python
BaseException
└── Exception
    ├── ValueError
    ├── TypeError
    ├── FileNotFoundError
    └── AppError (사용자 정의)
        ├── AuthError
        └── ValidationError
```

---

## 🧪 LAB 1 – 모의 퀴즈 (10:00 – 11:30)

아래 각 문제의 출력 결과를 **코드 실행 전에 예측**하고, 실행하여 확인하세요.

```python
# Q1. 출력 결과는?
x = [1, 2, 3]
y = x
y.append(4)
print(x)

# Q2. 출력 결과는?
def f(a, b=[]):
    b.append(a)
    return b
print(f(1))
print(f(2))
print(f(3, []))

# Q3. 출력 결과는?
data = {"a":1, "b":2, "c":3}
result = {v: k for k, v in data.items() if v > 1}
print(result)

# Q4. 출력 결과는?
def outer():
    x = 10
    def inner():
        nonlocal x
        x += 5
        return x
    return inner
f = outer()
print(f(), f(), f())

# Q5. 출력 결과는?
try:
    lst = [1, 2, 3]
    print(lst[5])
except IndexError:
    print("A")
except Exception:
    print("B")
else:
    print("C")
finally:
    print("D")
```

---

## 🧪 LAB 2 – 코드 리팩터링 실습 (11:30 – 13:00)

아래 나쁜 코드를 좋은 코드로 리팩터링하세요.

```python
# ❌ 리팩터링 전 – 중복, 비효율, 오류 처리 없음
def get_user_info(users, uid):
    found = None
    for u in users:
        if u['id'] == uid:
            found = u
    if found != None:
        n = found['name']
        a = found['age']
        e = found['email']
        print('이름: ' + n)
        print('나이: ' + str(a))
        print('이메일: ' + e)
    else:
        print('없음')
```

```python
# ✅ 리팩터링 목표 – 아래 조건을 반영하여 완성하세요
# 1. 타입 힌트 추가
# 2. 딕셔너리 lookup으로 O(n) → O(1) 개선
# 3. f-string 활용
# 4. NotFoundError 예외 발생
# 5. 독스트링 추가

class UserNotFoundError(Exception): ...

def get_user_info(users: list[dict], uid: int) -> dict:
    """..."""  # 완성하세요
```

---

## 🧪 LAB 3 – Phase 1 통합 도전 과제 (14:00 – 17:00)

**도서관 관리 CLI 시스템**을 처음부터 설계·구현하세요.

### 요구사항

```
books.json 파일에 도서 정보 저장

지원 기능:
  add    <isbn> <제목> <저자> <수량>  도서 추가
  list                                전체 도서 목록
  search <키워드>                     제목/저자 검색
  borrow <isbn> <회원ID>              대출 (-1권)
  return <isbn> <회원ID>              반납 (+1권)
  status <isbn>                       대출 현황
```

```python
# Book 구조 예시
{
  "isbn": "978-3-16-148410-0",
  "title": "파이썬 프로그래밍",
  "author": "홍길동",
  "stock": 3,
  "borrowed_by": []
}
```

### 평가 기준

| 항목 | 배점 |
|------|------|
| 패키지 구조 분리 | 20 |
| JSON 파일 I/O | 20 |
| 예외처리 적절성 | 20 |
| CLI 기능 완성도 | 20 |
| 코드 가독성 | 20 |

---

## 📝 자기 평가 (17:00 – 18:00)

아래 항목을 스스로 평가하세요 (1–5점).

| 개념 | 자신감 | 보완 필요 사항 |
|------|--------|----------------|
| 변수·자료형 | /5 | |
| 조건문·반복문 | /5 | |
| 함수 (*args, **kwargs) | /5 | |
| list / dict / set | /5 | |
| 파일 I/O & JSON | /5 | |
| 예외처리 | /5 | |
| 모듈·패키지 | /5 | |
| 프로젝트 구조 | /5 | |

**총점**: /40점

- **35점 이상**: Phase 2 진행 준비 완료 ✅
- **25–34점**: 취약 부분 복습 후 진행 ⚠️
- **25점 미만**: 강사와 1:1 보충 수업 권장 ❌

---

## ✅ Phase 1 최종 체크리스트

- [ ] 모의 퀴즈 5문제 정답 확인
- [ ] 코드 리팩터링 완성
- [ ] 도서관 관리 시스템 완성
- [ ] 자기 평가 완료
- [ ] Phase 2 예습 (클래스, OOP 개념 검색)

🔎 유튜브 관련 영상 검색: https://www.youtube.com/results?search_query=python+trading+day20+review
