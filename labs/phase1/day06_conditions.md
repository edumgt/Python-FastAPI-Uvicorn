# Day 06 – 조건문

> **소요시간**: 8시간 | **Phase**: 1 – Python 완전 기초

---

## 🎯 학습 목표

- `if / elif / else` 구문 완전 활용
- 중첩 조건문(nested if) 이해
- 삼항 연산자(조건 표현식) 활용
- `match-case` 문법(Python 3.10+) 소개

---

## 📖 이론 (08:00 – 10:00)

```python
# 기본 if/elif/else
score = 85
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
else:
    grade = "F"
print(f"학점: {grade}")

# 삼항 연산자
result = "합격" if score >= 60 else "불합격"

# match-case (Python 3.10+)
command = "quit"
match command:
    case "start":
        print("시작!")
    case "stop" | "quit":
        print("종료!")
    case _:
        print(f"알 수 없는 명령: {command}")
```

---

## 🧪 LAB 1 – 성적 처리 시스템 (10:00 – 12:00)

```python
# day06_grade.py

def get_grade(score: float) -> tuple[str, str]:
    """점수 → (학점, 코멘트) 반환"""
    if not 0 <= score <= 100:
        raise ValueError(f"유효하지 않은 점수: {score}")
    if score >= 95:   return "A+", "탁월합니다! 🏆"
    elif score >= 90: return "A",  "우수합니다! ⭐"
    elif score >= 85: return "B+", "좋습니다! 👍"
    elif score >= 80: return "B",  "양호합니다."
    elif score >= 75: return "C+", "보통입니다."
    elif score >= 70: return "C",  "노력이 필요합니다."
    elif score >= 60: return "D",  "많은 노력이 필요합니다."
    else:             return "F",  "재수강 권장."

test_scores = [98, 91, 86, 82, 76, 71, 65, 45, -5, 110]
for s in test_scores:
    try:
        grade, comment = get_grade(s)
        print(f"{s:5.1f}점 → {grade:<3} {comment}")
    except ValueError as e:
        print(f"오류: {e}")
```

---

## 🧪 LAB 2 – 자판기 시뮬레이터 (13:00 – 15:00)

```python
# day06_vending.py

menu = {
    1: ("아메리카노", 2000),
    2: ("카페라떼",   2500),
    3: ("오렌지주스", 1800),
    4: ("물",         800),
}

print("=== 자판기 ===")
for num, (name, price) in menu.items():
    print(f"{num}. {name:<12} {price:,}원")

choice = int(input("\n번호를 선택하세요: "))
money  = int(input("돈을 넣으세요: "))

if choice not in menu:
    print("잘못된 선택입니다.")
else:
    name, price = menu[choice]
    if money < price:
        print(f"잔액이 부족합니다. {price - money:,}원 더 필요합니다.")
    else:
        change = money - price
        print(f"\n{name} 나왔습니다! ☕")
        print(f"거스름돈: {change:,}원")
```

---

## 🧪 LAB 3 – match-case 계산기 (15:00 – 17:00)

```python
# day06_match.py

def calculate(a: float, op: str, b: float) -> float | str:
    match op:
        case "+": return a + b
        case "-": return a - b
        case "*": return a * b
        case "/":
            if b == 0:
                return "Error: 0으로 나누기"
            return a / b
        case "**": return a ** b
        case "%":
            if b == 0:
                return "Error: 0으로 나머지 연산"
            return a % b
        case _:
            return f"알 수 없는 연산자: {op}"

operations = [(10, "+", 3), (10, "-", 3), (10, "*", 3),
              (10, "/", 3), (10, "/", 0), (10, "**", 2), (10, "%", 3)]
for a, op, b in operations:
    result = calculate(a, op, b)
    print(f"{a} {op} {b} = {result}")
```

---

## 📝 과제 (17:00 – 18:00)

`day06_homework.py` – 로그인 검증기

1. `users` 딕셔너리 정의: `{"admin": "admin123", "user1": "pass1"}`
2. 사용자로부터 아이디/비밀번호 입력
3. 조건에 따라 메시지 출력:
   - 아이디 없음 / 비밀번호 틀림 / 로그인 성공
4. `admin` 계정 로그인 시 `"관리자 모드 진입"` 추가 출력

---

## ✅ 체크리스트

- [ ] `if/elif/else` 성적 처리 완성
- [ ] 자판기 시뮬레이터 완성
- [ ] `match-case` 계산기 완성
- [ ] 로그인 검증기 과제 완성
