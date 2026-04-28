# Day 12 – 딕셔너리

> **소요시간**: 8시간 | **Phase**: 1 – Python 완전 기초

---

## 🎯 학습 목표

- 딕셔너리 CRUD 전체 메서드 숙달
- 중첩 딕셔너리 처리
- 딕셔너리 컴프리헨션
- `get()`, `setdefault()`, `update()`, `pop()` 활용

---

## 📖 이론 (08:00 – 10:00)

```python
# 생성
person = {"name":"홍길동", "age":25, "city":"서울"}
empty  = {}
from_keys = dict.fromkeys(["a","b","c"], 0)  # {'a':0,'b':0,'c':0}

# CRUD
person["job"] = "개발자"           # 추가/수정
person.update({"age":26, "email":"hong@test.com"})
del person["city"]
removed = person.pop("email", "없음")  # 없으면 기본값 반환
person.setdefault("level", 1)      # 없을 때만 추가

# 조회
keys   = list(person.keys())
values = list(person.values())
items  = list(person.items())
val    = person.get("name", "Unknown")  # 안전한 접근

# 컴프리헨션
squares = {x: x**2 for x in range(1, 6)}
# {1:1, 2:4, 3:9, 4:16, 5:25}

# 중첩 딕셔너리
db = {
    "user1": {"name":"홍길동", "scores":[85,92,78]},
    "user2": {"name":"김철수", "scores":[91,88,95]},
}
avg = sum(db["user1"]["scores"]) / len(db["user1"]["scores"])
```

---

## 🧪 LAB 1 – 전화번호부 (10:00 – 12:00)

```python
# day12_phonebook.py
import json

phonebook: dict[str, dict] = {}

def add_contact(name: str, phone: str, email: str = "") -> None:
    phonebook[name] = {"phone": phone, "email": email}
    print(f"✅ '{name}' 추가됨")

def find_contact(name: str) -> dict | None:
    return phonebook.get(name)

def delete_contact(name: str) -> bool:
    return phonebook.pop(name, None) is not None

def search_by_phone(prefix: str) -> list[str]:
    return [name for name, info in phonebook.items()
            if info["phone"].startswith(prefix)]

def show_all() -> None:
    if not phonebook:
        print("  (비어있음)")
        return
    for name, info in sorted(phonebook.items()):
        print(f"  {name:<10} | {info['phone']:<15} | {info.get('email','')}")

# 테스트
add_contact("홍길동", "010-1234-5678", "hong@example.com")
add_contact("김철수", "010-9876-5432")
add_contact("이영희", "010-1111-2222", "lee@test.com")
print("\n전체:"); show_all()
print("\n010-1 으로 시작:", search_by_phone("010-1"))
print("\n홍길동 검색:", find_contact("홍길동"))
delete_contact("김철수")
print("\n김철수 삭제 후:"); show_all()
```

---

## 🧪 LAB 2 – 단어 빈도 분석기 (13:00 – 15:00)

```python
# day12_word_freq.py
from collections import defaultdict

text = """
Python is a high-level programming language. Python is widely used in
web development data science and artificial intelligence. Python syntax
is simple and readable making it great for beginners.
"""

def word_frequency(text: str) -> dict[str, int]:
    freq = defaultdict(int)
    for word in text.lower().split():
        word = word.strip(".,!?;:")
        if word:
            freq[word] += 1
    return dict(freq)

freq = word_frequency(text)

# 상위 10개 단어
top10 = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:10]
print("=== 단어 빈도 Top 10 ===")
for rank, (word, count) in enumerate(top10, 1):
    bar = "█" * count
    print(f"{rank:2d}. {word:<15} {count:3d} {bar}")

# 딕셔너리 컴프리헨션 – 3회 이상 등장 단어만
common = {w: c for w, c in freq.items() if c >= 3}
print(f"\n3회 이상 등장: {common}")
```

---

## 🧪 LAB 3 – 중첩 딕셔너리: 학교 DB (15:00 – 17:00)

```python
# day12_school_db.py

school = {
    "1학년": {
        "1반": [{"name":"홍길동","score":85},{"name":"김철수","score":92}],
        "2반": [{"name":"이영희","score":78},{"name":"박민준","score":95}],
    },
    "2학년": {
        "1반": [{"name":"최수진","score":88},{"name":"강동원","score":73}],
    }
}

# 전체 학생 평균
all_scores = [s["score"]
              for grade in school.values()
              for cls in grade.values()
              for s in cls]
print(f"전교 평균: {sum(all_scores)/len(all_scores):.1f}점")

# 학년별 평균
for grade_name, classes in school.items():
    scores = [s["score"] for cls in classes.values() for s in cls]
    print(f"{grade_name} 평균: {sum(scores)/len(scores):.1f}점")

# 90점 이상 학생
top = [(s["name"], grade_name, cls_name)
       for grade_name, classes in school.items()
       for cls_name, students in classes.items()
       for s in students if s["score"] >= 90]
print(f"\n90점 이상: {top}")
```

---

## 📝 과제 (17:00 – 18:00)

`day12_homework.py` – JSON 기반 상품 재고 관리

1. `inventory.json` 파일에 상품 데이터(name, price, stock) 저장
2. 추가·조회·재고 차감·삭제 함수 구현
3. 재고 5개 미만 상품 경고 출력
4. 전체 재고 가치(price × stock 합계) 출력

---

## ✅ 체크리스트

- [ ] 딕셔너리 CRUD 메서드 전부 사용
- [ ] `get()`, `setdefault()`, `pop()` 활용
- [ ] 전화번호부 CRUD 완성
- [ ] 단어 빈도 Top 10 분석 완성
- [ ] 중첩 딕셔너리 학교 DB 처리 완성
- [ ] JSON 상품 재고 관리 과제 완성
