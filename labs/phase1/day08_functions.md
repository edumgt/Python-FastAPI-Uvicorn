# Day 08 – 함수 기초

> **소요시간**: 8시간 | **Phase**: 1 – Python 완전 기초

---

## 🎯 학습 목표

- `def` 로 함수 정의, `return` 으로 값 반환
- 매개변수(parameter) vs 인자(argument) 구분
- 기본값 매개변수, 키워드 인자
- 함수 독스트링(docstring) 작성

---

## 📖 이론 (08:00 – 10:00)

```python
def greet(name: str, greeting: str = "안녕하세요") -> str:
    """
    인사 메시지를 반환합니다.

    Args:
        name: 이름
        greeting: 인사말 (기본값: "안녕하세요")
    Returns:
        str: 인사 메시지
    """
    return f"{greeting}, {name}님!"

# 호출 방식
print(greet("홍길동"))                        # 기본값 사용
print(greet("이순신", "반갑습니다"))          # 위치 인자
print(greet(greeting="좋은 아침", name="신사임당")) # 키워드 인자

# 다중 반환값
def min_max(numbers: list[int]) -> tuple[int, int]:
    return min(numbers), max(numbers)

lo, hi = min_max([3, 1, 4, 1, 5, 9, 2, 6])
print(f"최솟값: {lo}, 최댓값: {hi}")
```

---

## 🧪 LAB 1 – 수학 함수 구현 (10:00 – 12:00)

```python
# day08_math_funcs.py

def factorial(n: int) -> int:
    """n! 계산 (반복문 버전)"""
    if n < 0:
        raise ValueError("음수는 계산 불가")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def power(base: float, exp: int) -> float:
    """base ** exp 직접 구현"""
    result = 1.0
    for _ in range(abs(exp)):
        result *= base
    return result if exp >= 0 else 1 / result

def gcd(a: int, b: int) -> int:
    """유클리드 호제법으로 최대공약수"""
    while b:
        a, b = b, a % b
    return a

def lcm(a: int, b: int) -> int:
    """최소공배수 = a*b / gcd(a,b)"""
    return a * b // gcd(a, b)

# 테스트
for n in range(0, 8):
    print(f"{n}! = {factorial(n)}")
print(f"\ngcd(48, 18) = {gcd(48, 18)}")
print(f"lcm(12, 8)  = {lcm(12, 8)}")
```

---

## 🧪 LAB 2 – 온도 변환기 (13:00 – 15:00)

```python
# day08_temp.py

def celsius_to_fahrenheit(c: float) -> float:
    return c * 9/5 + 32

def fahrenheit_to_celsius(f: float) -> float:
    return (f - 32) * 5/9

def celsius_to_kelvin(c: float) -> float:
    return c + 273.15

def kelvin_to_celsius(k: float) -> float:
    if k < 0:
        raise ValueError("켈빈은 0 미만이 될 수 없습니다.")
    return k - 273.15

# 변환 테이블
print(f"{'섭씨':>8} {'화씨':>10} {'켈빈':>10}")
print("-" * 32)
for c in range(-20, 105, 10):
    f = celsius_to_fahrenheit(c)
    k = celsius_to_kelvin(c)
    print(f"{c:>7}°C {f:>9.1f}°F {k:>9.2f}K")
```

---

## 🧪 LAB 3 – 함수로 분리 리팩터링 (15:00 – 17:00)

아래 절차형 코드를 **함수 5개로 분리**하여 리팩터링하세요.

```python
# 리팩터링 전 (절차형)
data = [85, 92, 78, 95, 88, 74, 91, 67, 80, 83]
total = sum(data)
avg = total / len(data)
highest = max(data)
lowest = min(data)
passed = [s for s in data if s >= 75]
print(f"평균: {avg:.1f}, 최고: {highest}, 최저: {lowest}, 합격: {len(passed)}명")
```

```python
# 리팩터링 후 – 각 함수를 구현하세요
def calculate_average(scores): ...
def find_highest(scores): ...
def find_lowest(scores): ...
def get_passed(scores, threshold=75): ...
def print_report(scores): ...

data = [85, 92, 78, 95, 88, 74, 91, 67, 80, 83]
print_report(data)
```

---

## 📝 과제 (17:00 – 18:00)

`day08_homework.py` – 이자 계산기

1. `simple_interest(principal, rate, years)` – 단리 계산
2. `compound_interest(principal, rate, years, n=1)` – 복리 계산 (n: 연간 복리 횟수)
3. 원금 1,000,000원, 연 5%, 10년 기준으로 두 방식 비교 출력

---

## ✅ 체크리스트

- [ ] `def`, `return`, 독스트링 형식 준수
- [ ] 기본값/키워드 인자 활용
- [ ] 수학 함수 4개 구현
- [ ] 온도 변환 테이블 출력
- [ ] 절차형 코드 함수 분리 리팩터링 완성
- [ ] 이자 계산기 과제 완성

🔎 유튜브 관련 영상 검색: https://www.youtube.com/results?search_query=python+trading+day08+functions
