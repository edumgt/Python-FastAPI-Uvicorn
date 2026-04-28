# Day 05 – 문자열 심화

> **소요시간**: 8시간 | **Phase**: 1 – Python 완전 기초

---

## 🎯 학습 목표

- 문자열 슬라이싱 `[start:stop:step]` 완전 이해
- 주요 문자열 메서드 20가지 이상 활용
- 문자열 불변성(immutable) 개념 이해
- 멀티라인 문자열 및 이스케이프 시퀀스 처리

---

## 📖 이론 (08:00 – 10:00)

### 슬라이싱

```python
s = "Hello, Python!"
#    0123456789...
print(s[0])       # 'H'
print(s[-1])      # '!'
print(s[0:5])     # 'Hello'
print(s[7:])      # 'Python!'
print(s[:5])      # 'Hello'
print(s[::2])     # 'Hlo yhn'
print(s[::-1])    # '!nohtyP ,olleH'  (뒤집기)
```

### 핵심 메서드

```python
s = "  Hello, Python!  "
print(s.strip())           # "Hello, Python!"      양쪽 공백 제거
print(s.lower())           # "  hello, python!  "  소문자 변환
print(s.upper())           # "  HELLO, PYTHON!  "  대문자 변환
print(s.replace("Python", "World"))  # 치환
print(s.split(", "))       # ['  Hello', 'Python!  ']  분리
print(", ".join(["a","b","c"]))      # 'a, b, c'     합치기
print(s.find("Python"))    # 8 (없으면 -1)
print("Python" in s)       # True
print(s.startswith("  H")) # True
print(s.count("l"))        # 2
print(s.zfill(25))         # 0으로 왼쪽 채우기 (숫자 문자열용)
```

---

## 🧪 LAB 1 – 슬라이싱 실습 (10:00 – 12:00)

```python
# day05_slicing.py

text = "Python Programming"

# 다양한 슬라이싱 결과 예측 후 확인
slices = [
    text[0:6],
    text[-11:],
    text[::2],
    text[::-1],
    text[7:18:2],
]
for s in slices:
    print(repr(s))

# 팰린드롬 검사 함수
def is_palindrome(word: str) -> bool:
    word = word.lower().replace(" ", "")
    return word == word[::-1]

words = ["racecar", "hello", "madam", "python", "level"]
for w in words:
    print(f"'{w}' → {'팰린드롬 ✅' if is_palindrome(w) else '아님 ❌'}")
```

---

## 🧪 LAB 2 – 문자열 메서드 체인 (13:00 – 15:00)

```python
# day05_methods.py

# 이메일 유효성 간단 검사
def simple_email_check(email: str) -> bool:
    email = email.strip().lower()
    return "@" in email and email.count("@") == 1 and "." in email.split("@")[1]

emails = ["user@example.com", "bad-email", "a@b.c", "two@@email.com", "  test@test.org  "]
for e in emails:
    status = "유효 ✅" if simple_email_check(e) else "무효 ❌"
    print(f"{e!r:<30} → {status}")

# CSV 파싱 흉내 내기
csv_line = "홍길동,25,서울,개발자"
fields = csv_line.split(",")
person = {
    "name": fields[0],
    "age":  int(fields[1]),
    "city": fields[2],
    "job":  fields[3],
}
print(person)
```

---

## 🧪 LAB 3 – 도전: 문자열 통계 분석기 (15:00 – 17:00)

사용자로부터 임의의 문장을 입력받아 아래 통계를 출력하는 `text_stats.py`를 완성하세요.

```
문장: The quick brown fox jumps over the lazy dog

--- 문자열 통계 ---
전체 길이      : 43
단어 수        : 9
고유 단어 수   : 8  (중복 제외)
가장 긴 단어   : jumps (5글자)
소문자 수      : 35
대문자 수      : 1
공백 수        : 8
```

힌트: `.split()`, `set()`, `max()`, `.islower()`, `.isupper()`, `.isspace()`

---

## 📝 과제 (17:00 – 18:00)

`day05_homework.py` – 이니셜 생성기

1. 사용자로부터 영문 전체 이름을 입력받으세요. (예: `John Michael Doe`)
2. 각 단어의 첫 글자를 대문자로 추출해 이니셜을 만드세요. (예: `J.M.D.`)
3. 이름을 역순으로 출력하세요. (예: `eoD leahciM nhoJ`)
4. 이름이 팰린드롬인지 검사하세요. (공백 무시, 대소문자 무시)

---

## ✅ 체크리스트

- [ ] `[start:stop:step]` 슬라이싱 6가지 이상 실습
- [ ] 팰린드롬 검사 함수 완성
- [ ] 이메일 유효성 검사 완성
- [ ] CSV 파싱 딕셔너리 변환
- [ ] 문자열 통계 분석기 완성
- [ ] 이니셜 생성기 과제 완성

---

## 📚 참고자료

- [str 메서드 공식 문서](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)
