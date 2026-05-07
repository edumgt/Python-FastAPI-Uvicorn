# Day 02 – Hello World & 출력 함수

> **소요시간**: 8시간 | **Phase**: 1 – Python 완전 기초

---

## 🎯 학습 목표

- `print()` 함수의 다양한 옵션 활용
- f-string, `.format()`, `%` 포매팅 차이 이해
- 주석 작성 방법 (`#`, `"""`)
- 기본 입력 함수 `input()` 사용

---

## 📖 이론 (08:00 – 10:00)

### 1. print() 기본 옵션

```python
print("Hello")                     # 기본 출력
print("Hello", "World")            # 여러 값 (sep 기본값: ' ')
print("Hello", "World", sep=", ")  # 구분자 변경
print("Hello", end="!\n")          # 줄 끝 문자 변경
print()                            # 빈 줄 출력
```

### 2. 문자열 포매팅 3가지

```python
name = "홍길동"
score = 95.5

# 1) f-string (권장 – Python 3.6+)
print(f"이름: {name}, 점수: {score:.1f}")

# 2) .format()
print("이름: {}, 점수: {:.1f}".format(name, score))

# 3) % 포매팅 (구버전 스타일)
print("이름: %s, 점수: %.1f" % (name, score))
```

### 3. 주석

```python
# 한 줄 주석

"""
여러 줄 주석(독스트링)
함수·클래스 설명에 주로 사용
"""
```

---

## 🧪 LAB 1 – print 심화 (10:00 – 12:00)

`day02_print.py` 를 만들고 아래 코드를 실습하세요.

```python
# day02_print.py

# 1. 기본 출력
print("Hello, World!")

# 2. sep / end 활용
print("2026", "04", "28", sep="-")
print("로딩중", end="")
print(".", end="")
print(".", end="")
print(".")

# 3. f-string 포매팅
name = "파이썬"
version = 3.10
print(f"언어: {name} | 버전: {version}")

# 4. 숫자 포매팅
pi = 3.14159265
print(f"π ≈ {pi:.2f}")        # 소수 2자리
print(f"π ≈ {pi:10.4f}")      # 너비 10, 소수 4자리
print(f"{1000000:,}")          # 천 단위 구분자

# 5. 정렬
print(f"{'왼쪽':<10}|")        # 왼쪽 정렬
print(f"{'오른쪽':>10}|")      # 오른쪽 정렬
print(f"{'가운데':^10}|")      # 가운데 정렬
```

---

## 🧪 LAB 2 – input() 활용 (13:00 – 15:00)

```python
# day02_input.py

# 기본 입력
name = input("이름을 입력하세요: ")
age = int(input("나이를 입력하세요: "))

print(f"\n안녕하세요, {name}님!")
print(f"내년에는 {age + 1}살이 됩니다.")

# 간단한 계산기
print("\n=== 간단 계산기 ===")
a = float(input("첫 번째 숫자: "))
b = float(input("두 번째 숫자: "))
print(f"{a} + {b} = {a + b}")
print(f"{a} - {b} = {a - b}")
print(f"{a} × {b} = {a * b}")
if b != 0:
    print(f"{a} ÷ {b} = {a / b:.4f}")
else:
    print("0으로 나눌 수 없습니다.")
```

---

## 🧪 LAB 3 – 도전 과제: 영수증 출력기 (15:00 – 17:00)

아래 출력 형식과 동일하게 영수증을 출력하는 `receipt.py`를 작성하세요.

**예상 출력 형식**:
```
=============================
       🛒 영수증
=============================
상품명          수량    금액
-----------------------------
아메리카노        2    9,000
카페라떼          1    5,500
치즈케이크        3   18,000
-----------------------------
합계                  32,500
VAT (10%)              3,250
=============================
최종 결제금액         35,750
=============================
```

힌트:
```python
items = [
    ("아메리카노", 2, 4500),
    ("카페라떼",   1, 5500),
    ("치즈케이크", 3, 6000),
]
for name, qty, price in items:
    total = qty * price
    print(f"{name:<12}{qty:>4}{total:>10,}")
```

---

## 📝 과제 (17:00 – 18:00)

`day02_homework.py`를 작성하세요.

1. 사용자로부터 **이름**, **나이**, **직업**을 입력받으세요.
2. 아래 형식으로 출력하세요.

```
╔══════════════════════╗
║     나의 명함        ║
╠══════════════════════╣
║ 이름: 홍길동         ║
║ 나이: 25세           ║
║ 직업: 개발자         ║
╚══════════════════════╝
```

---

## ✅ 체크리스트

- [ ] `print()` sep, end 옵션 이해
- [ ] f-string 숫자 포매팅 (소수점, 정렬, 천 단위) 적용
- [ ] `input()` 으로 값 입력 및 형변환
- [ ] 영수증 LAB 3 완성
- [ ] 과제 명함 출력기 완성

---

## 📚 참고자료

- [Python print() 공식 문서](https://docs.python.org/3/library/functions.html#print)
- [f-string 치트시트](https://fstring.help/cheat/)

🔎 유튜브 관련 영상 검색: https://www.youtube.com/results?search_query=python+trading+day02+hello
