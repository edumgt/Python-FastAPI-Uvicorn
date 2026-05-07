# Day 09 – 함수 심화

> **소요시간**: 8시간 | **Phase**: 1 – Python 완전 기초

---

## 🎯 학습 목표

- `*args`, `**kwargs` 가변 인자 활용
- 스코프 규칙 (LEGB: Local → Enclosing → Global → Built-in)
- `global`, `nonlocal` 키워드 이해
- 함수를 값처럼 사용 (일급 함수, 고차 함수 입문)

---

## 📖 이론 (08:00 – 10:00)

```python
# *args – 가변 위치 인자
def sum_all(*args):
    return sum(args)

print(sum_all(1, 2, 3))           # 6
print(sum_all(1, 2, 3, 4, 5))     # 15

# **kwargs – 가변 키워드 인자
def show_info(**kwargs):
    for key, val in kwargs.items():
        print(f"  {key}: {val}")

show_info(name="홍길동", age=25, city="서울")

# 혼합 사용
def mixed(a, b, *args, sep=", ", **kwargs):
    print(f"a={a}, b={b}, args={args}, sep={sep!r}, kwargs={kwargs}")

mixed(1, 2, 3, 4, sep=" | ", x=10, y=20)

# 스코프
x = "global"
def outer():
    x = "enclosing"
    def inner():
        x = "local"
        print(x)    # local
    inner()
    print(x)        # enclosing
outer()
print(x)            # global
```

---

## 🧪 LAB 1 – *args/**kwargs 활용 (10:00 – 12:00)

```python
# day09_args.py

def describe_product(name: str, price: float, *features, **specs) -> None:
    """상품 정보를 출력합니다."""
    print(f"\n{'='*40}")
    print(f"상품명: {name} | 가격: {price:,.0f}원")
    if features:
        print("특징:", ", ".join(features))
    if specs:
        print("스펙:")
        for k, v in specs.items():
            print(f"  {k}: {v}")
    print("="*40)

describe_product("노트북", 1500000, "가볍다", "빠르다",
                 CPU="Intel i7", RAM="16GB", SSD="512GB")
describe_product("마우스", 35000, "무선", color="검정", DPI=1600)

# 스프레드 연산자 (**) 활용
def create_user(name, age, city):
    return {"name": name, "age": age, "city": city}

data = {"name": "이순신", "age": 30, "city": "서울"}
user = create_user(**data)  # 딕셔너리 언패킹
print(user)
```

---

## 🧪 LAB 2 – 클로저 입문 (13:00 – 15:00)

```python
# day09_closure.py

# 클로저: 바깥 함수의 변수를 기억하는 내부 함수
def make_counter(start: int = 0, step: int = 1):
    count = start
    def counter():
        nonlocal count
        current = count
        count += step
        return current
    return counter

c1 = make_counter()
c2 = make_counter(start=100, step=10)

print([c1() for _ in range(5)])   # [0,1,2,3,4]
print([c2() for _ in range(5)])   # [100,110,120,130,140]

# 함수 팩토리
def make_power(exp: int):
    def power(base: float) -> float:
        return base ** exp
    return power

square = make_power(2)
cube   = make_power(3)
print(list(map(square, [1,2,3,4,5])))  # [1,4,9,16,25]
print(list(map(cube,   [1,2,3,4,5])))  # [1,8,27,64,125]
```

---

## 🧪 LAB 3 – 고차 함수 (15:00 – 17:00)

```python
# day09_higher_order.py

from functools import reduce

data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# map: 변환
doubled  = list(map(lambda x: x * 2, data))
squared  = list(map(lambda x: x ** 2, data))

# filter: 필터
evens = list(filter(lambda x: x % 2 == 0, data))
odds  = list(filter(lambda x: x % 2 != 0, data))

# reduce: 집계
total   = reduce(lambda a, b: a + b, data)
product = reduce(lambda a, b: a * b, data)

print(f"doubled : {doubled}")
print(f"squared : {squared}")
print(f"evens   : {evens}")
print(f"odds    : {odds}")
print(f"합계    : {total}")
print(f"곱      : {product}")

# 함수를 인자로 받는 함수
def apply_twice(func, value):
    return func(func(value))

print(apply_twice(lambda x: x + 3, 7))   # 13
print(apply_twice(lambda x: x * 2, 5))   # 20
```

---

## 📝 과제 (17:00 – 18:00)

`day09_homework.py` – 유연한 통계 함수

- `stats(*numbers, mode="all")` 함수를 구현하세요.
- `mode="all"` → 합계·평균·최대·최소 모두 출력
- `mode="avg"` → 평균만 반환
- `mode="sum"` → 합계만 반환
- 아무 숫자도 없으면 `ValueError` 발생

---

## ✅ 체크리스트

- [ ] `*args`, `**kwargs` 혼합 함수 구현
- [ ] 딕셔너리 언패킹(`**`) 활용
- [ ] 클로저와 `nonlocal` 이해
- [ ] `make_power` 함수 팩토리 완성
- [ ] `map/filter/reduce` 활용
- [ ] 유연한 통계 함수 과제 완성

🔎 유튜브 관련 영상 검색: https://www.youtube.com/results?search_query=python+trading+day09+advanced+functions
