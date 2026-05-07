# Day 03 – 변수와 자료형

> **소요시간**: 8시간 | **Phase**: 1 – Python 완전 기초

---

## 🎯 학습 목표

- Python 기본 자료형 6가지 이해 및 활용
- `type()`, `isinstance()` 로 타입 확인
- 형변환(type casting) 이해
- 변수 명명 규칙 및 네이밍 컨벤션

---

## 📖 이론 (08:00 – 10:00)

### 1. 기본 자료형

| 자료형 | 키워드 | 예시 |
|--------|--------|------|
| 정수 | `int` | `42`, `-7`, `0` |
| 실수 | `float` | `3.14`, `-0.5`, `1e10` |
| 문자열 | `str` | `"hello"`, `'world'` |
| 불리언 | `bool` | `True`, `False` |
| 없음 | `NoneType` | `None` |
| 복소수 | `complex` | `3+4j` |

### 2. 변수 명명 규칙

```python
# 올바른 변수명
user_name = "홍길동"      # snake_case (권장)
userName = "홍길동"       # camelCase (비권장)
MAX_SIZE = 100            # 상수는 대문자

# 잘못된 변수명
# 1name = "오류"          # 숫자로 시작 불가
# my-var = "오류"         # 하이픈 불가
# class = "오류"          # 예약어 불가
```

### 3. 형변환

```python
int("42")      # → 42
float("3.14")  # → 3.14
str(100)       # → "100"
bool(0)        # → False
bool("")       # → False (falsy 값)
bool("hi")     # → True
```

---

## 🧪 LAB 1 – 자료형 탐구 (10:00 – 12:00)

```python
# day03_types.py

# 각 자료형 생성 및 type() 확인
n = 42
f = 3.14
s = "Python"
b = True
none_val = None
c = 2 + 3j

print(f"n={n},  type={type(n)}")
print(f"f={f},  type={type(f)}")
print(f"s={s},  type={type(s)}")
print(f"b={b},  type={type(b)}")
print(f"none={none_val}, type={type(none_val)}")
print(f"c={c},  type={type(c)}")

# isinstance 활용
print("\n--- isinstance 확인 ---")
print(isinstance(n, int))          # True
print(isinstance(f, (int, float))) # True (int 또는 float)
print(isinstance(s, str))          # True
```

---

## 🧪 LAB 2 – Falsy / Truthy & 형변환 (13:00 – 15:00)

```python
# day03_casting.py

# Falsy 값 목록
falsy_values = [0, 0.0, "", [], {}, set(), None, False]
print("=== Falsy 값 ===")
for v in falsy_values:
    print(f"  bool({repr(v)}) → {bool(v)}")

# 형변환 실습
print("\n=== 형변환 ===")
print(int("100"))       # str → int
print(float("3.14"))    # str → float
print(str(255))         # int → str
print(int(3.99))        # float → int (내림, 반올림 아님)
print(int("FF", 16))    # 16진수 문자열 → int

# 오류 상황 확인
try:
    int("hello")
except ValueError as e:
    print(f"\nValueError 발생: {e}")
```

---

## 🧪 LAB 3 – 도전: 단위 변환기 (15:00 – 17:00)

사용자로부터 킬로미터(km)를 입력받아 다양한 단위로 변환하는 `converter.py`를 작성하세요.

```python
# converter.py

km = float(input("거리를 km 단위로 입력하세요: "))

meter = km * 1000
cm = km * 100000
mile = km * 0.621371
yard = km * 1093.61

print(f"\n=== {km} km 단위 변환 결과 ===")
print(f"미터(m)    : {meter:,.2f} m")
print(f"센티미터   : {cm:,.2f} cm")
print(f"마일(mile) : {mile:.4f} mile")
print(f"야드(yard) : {yard:,.2f} yard")
```

**추가 도전**: `int`, `float`, `str` 타입이 섞인 입력에 대해 예외 처리를 추가하세요.

---

## 📝 과제 (17:00 – 18:00)

`day03_homework.py` – 체질량지수(BMI) 계산기

1. 키(cm)와 몸무게(kg)를 입력받으세요.
2. BMI = 몸무게(kg) / (키(m))² 를 계산하세요.
3. 아래 기준으로 결과를 출력하세요.

| BMI | 판정 |
|-----|------|
| 18.5 미만 | 저체중 |
| 18.5 ~ 22.9 | 정상 |
| 23.0 ~ 24.9 | 과체중 |
| 25.0 이상 | 비만 |

```
키: 175 cm, 몸무게: 70 kg
BMI = 22.86
판정: 정상
```

---

## ✅ 체크리스트

- [ ] 6가지 기본 자료형 `type()` 출력 확인
- [ ] `isinstance()` 다중 타입 체크 활용
- [ ] Falsy 값 전체 이해
- [ ] 형변환 및 ValueError 처리 실습
- [ ] 단위 변환기 LAB 3 완성
- [ ] BMI 계산기 과제 완성

---

## 📚 참고자료

- [Python 내장 타입 공식 문서](https://docs.python.org/3/library/stdtypes.html)
- [Python 네이밍 컨벤션 PEP 8](https://peps.python.org/pep-0008/#naming-conventions)

🔎 유튜브 관련 영상 검색: https://www.youtube.com/results?search_query=python+trading+day03+datatypes
