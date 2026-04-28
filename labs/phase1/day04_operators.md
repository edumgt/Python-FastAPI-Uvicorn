# Day 04 – 연산자

> **소요시간**: 8시간 | **Phase**: 1 – Python 완전 기초

---

## 🎯 학습 목표

- 산술·비교·논리·비트·할당 연산자 이해
- 연산자 우선순위 파악
- `//`(몫), `%`(나머지), `**`(거듭제곱) 활용

---

## 📖 이론 (08:00 – 10:00)

### 산술 연산자

```python
a, b = 17, 5
print(a + b)   # 22 – 덧셈
print(a - b)   # 12 – 뺄셈
print(a * b)   # 85 – 곱셈
print(a / b)   # 3.4 – 나눗셈 (항상 float)
print(a // b)  # 3   – 정수 나눗셈(몫)
print(a % b)   # 2   – 나머지
print(a ** b)  # 1419857 – 거듭제곱
```

### 비교 연산자

```python
print(5 > 3)   # True
print(5 == 5)  # True
print(5 != 3)  # True
print(5 >= 5)  # True
# 체인 비교
print(1 < 3 < 5)  # True
```

### 논리 연산자

```python
print(True and False)  # False
print(True or False)   # True
print(not True)        # False
# 단락 평가(short-circuit)
x = None
print(x or "기본값")   # "기본값"
```

### 할당 연산자

```python
n = 10
n += 5   # n = 15
n -= 3   # n = 12
n *= 2   # n = 24
n //= 5  # n = 4
n **= 3  # n = 64
```

---

## 🧪 LAB 1 – 산술 연산 실습 (10:00 – 12:00)

```python
# day04_arithmetic.py

# 시계 문제: 3500초는 몇 시간, 몇 분, 몇 초인가?
total_seconds = 3500
hours   = total_seconds // 3600
minutes = (total_seconds % 3600) // 60
seconds = total_seconds % 60

print(f"{total_seconds}초 = {hours}시간 {minutes}분 {seconds}초")

# 홀짝 판별
for n in [0, 1, 7, 100, 333]:
    result = "짝수" if n % 2 == 0 else "홀수"
    print(f"{n:4d} → {result}")

# 제곱근 (** 0.5)
import math
numbers = [4, 9, 16, 25, 144]
for n in numbers:
    print(f"√{n} = {n ** 0.5:.2f}  (math: {math.sqrt(n):.2f})")
```

---

## 🧪 LAB 2 – 논리·비교 연산 (13:00 – 15:00)

```python
# day04_logic.py

# 윤년 판별 공식: (4의 배수) AND (100의 배수 아님 OR 400의 배수)
def is_leap_year(year: int) -> bool:
    return (year % 4 == 0) and (year % 100 != 0 or year % 400 == 0)

test_years = [1900, 2000, 2024, 2025, 2100]
for y in test_years:
    print(f"{y}년 → {'윤년 ✅' if is_leap_year(y) else '평년 ❌'}")

# 단락 평가 활용
values = [None, 0, "", "hello", 42]
for v in values:
    result = v or "기본값"
    print(f"  {repr(v)!s:<10} or '기본값' → {repr(result)}")
```

---

## 🧪 LAB 3 – 도전: 비트 연산 시각화 (15:00 – 17:00)

```python
# day04_bitwise.py

a, b = 0b1010, 0b1100   # 10, 12
print(f"a      = {a:08b} ({a})")
print(f"b      = {b:08b} ({b})")
print(f"a & b  = {(a & b):08b} ({a & b})")   # AND
print(f"a | b  = {(a | b):08b} ({a | b})")   # OR
print(f"a ^ b  = {(a ^ b):08b} ({a ^ b})")   # XOR
print(f"~a     = {(~a):08b} ({~a})")          # NOT
print(f"a << 1 = {(a << 1):08b} ({a << 1})")  # 왼쪽 시프트
print(f"a >> 1 = {(a >> 1):08b} ({a >> 1})")  # 오른쪽 시프트
```

---

## 📝 과제 (17:00 – 18:00)

`day04_homework.py` – 세금 계산기

1. 연 소득을 입력받아 아래 세율로 세금을 계산하세요.

| 과세표준 | 세율 |
|----------|------|
| 1,200만 이하 | 6% |
| 1,200만 ~ 4,600만 | 15% |
| 4,600만 ~ 8,800만 | 24% |
| 8,800만 초과 | 35% |

2. 결과: 연소득, 적용 세율, 납부 세금, 세후 소득을 출력하세요.

---

## ✅ 체크리스트

- [ ] `//`, `%`, `**` 연산자 활용
- [ ] 시계 계산 실습 완성
- [ ] 윤년 판별 논리 연산 완성
- [ ] 비트 연산 출력 완성
- [ ] 세금 계산기 과제 완성

---

## 📚 참고자료

- [Python 연산자 우선순위](https://docs.python.org/3/reference/expressions.html#operator-precedence)
