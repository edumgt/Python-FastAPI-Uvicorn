# Day 07 – 반복문

> **소요시간**: 8시간 | **Phase**: 1 – Python 완전 기초

---

## 🎯 학습 목표

- `for` 루프와 `range()` 완전 이해
- `while` 루프 활용
- `break`, `continue`, `else` 절 이해
- `enumerate()`, `zip()` 활용

---

## 📖 이론 (08:00 – 10:00)

```python
# for + range
for i in range(5):       print(i, end=" ")  # 0 1 2 3 4
for i in range(1,6):     print(i, end=" ")  # 1 2 3 4 5
for i in range(10,0,-2): print(i, end=" ")  # 10 8 6 4 2

# enumerate
fruits = ["apple","banana","cherry"]
for i, f in enumerate(fruits, start=1):
    print(f"{i}. {f}")

# zip
names  = ["홍길동","김철수","이영희"]
scores = [95, 82, 78]
for n, s in zip(names, scores):
    print(f"{n}: {s}점")

# while
n = 1
while n <= 5:
    print(n, end=" ")
    n += 1

# break / continue / else
for i in range(10):
    if i == 3: continue    # 3 건너뜀
    if i == 7: break       # 7에서 종료
    print(i, end=" ")
else:
    print("완료")  # break 없이 끝나면 실행
```

---

## 🧪 LAB 1 – 구구단 출력기 (10:00 – 12:00)

```python
# day07_gugu.py

# 전체 구구단 (2~9단)
for dan in range(2, 10):
    print(f"\n--- {dan}단 ---")
    for i in range(1, 10):
        print(f"{dan} × {i:2d} = {dan*i:2d}")

# 대각선 구구단 (피라미드 형태)
print("\n=== 피라미드 구구단 ===")
for i in range(1, 10):
    for j in range(1, i+1):
        print(f"{j}×{i}={i*j:2d}", end="  ")
    print()
```

---

## 🧪 LAB 2 – 패턴 출력 (13:00 – 15:00)

```python
# day07_pattern.py

n = 5

# 1. 오른쪽 삼각형
for i in range(1, n+1):
    print("*" * i)

# 2. 피라미드
for i in range(1, n+1):
    print(" " * (n-i) + "*" * (2*i-1))

# 3. 다이아몬드
for i in range(1, n+1):
    print(" " * (n-i) + "*" * (2*i-1))
for i in range(n-1, 0, -1):
    print(" " * (n-i) + "*" * (2*i-1))

# 4. 숫자 삼각형
for i in range(1, n+1):
    for j in range(1, i+1):
        print(j, end=" ")
    print()
```

---

## 🧪 LAB 3 – 소수 판별기 (15:00 – 17:00)

```python
# day07_primes.py
import math

def is_prime(n: int) -> bool:
    """n이 소수인지 판별"""
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True

# 1~100 사이 소수 목록
primes = [n for n in range(2, 101) if is_prime(n)]
print(f"1~100 소수 ({len(primes)}개):")
for i, p in enumerate(primes, 1):
    print(f"{p:4d}", end="\n" if i % 10 == 0 else "")

# 사용자 입력 소수 판별
num = int(input("\n소수 판별할 숫자 입력: "))
print(f"{num}은(는) {'소수 ✅' if is_prime(num) else '소수 아님 ❌'}")
```

---

## 📝 과제 (17:00 – 18:00)

`day07_homework.py` – FizzBuzz 확장판

1. 1~100 출력 (3의 배수 → "Fizz", 5의 배수 → "Buzz", 15의 배수 → "FizzBuzz")
2. 7의 배수이면서 짝수인 수의 합을 구하세요.
3. `enumerate`를 사용하여 각 항목에 번호를 붙여 출력하세요.

---

## ✅ 체크리스트

- [ ] `for/range` 구구단 완성
- [ ] `break/continue/else` 이해
- [ ] 패턴 출력 4종 완성
- [ ] 소수 판별 함수 완성
- [ ] FizzBuzz 확장판 완성
