# Day 13 – 셋(Set)

> **소요시간**: 8시간 | **Phase**: 1 – Python 완전 기초

---

## 🎯 학습 목표

- `set` 생성, 추가/제거 메서드 숙달
- 집합 연산: 합집합·교집합·차집합·대칭차집합
- `frozenset`(불변 셋) 이해
- 중복 제거 실용 패턴 활용

---

## 📖 이론 (08:00 – 10:00)

```python
# 생성
fruits = {"apple", "banana", "orange"}
nums   = set([1, 2, 2, 3, 3, 3])  # {1,2,3} (중복 제거)
empty  = set()                     # {}는 dict! set()으로 생성

# CRUD
fruits.add("grape")
fruits.update(["mango","kiwi"])
fruits.remove("banana")      # 없으면 KeyError
fruits.discard("durian")     # 없어도 오류 없음
popped = fruits.pop()        # 임의 요소 제거·반환

# 집합 연산
A = {1,2,3,4,5}
B = {3,4,5,6,7}
print(A | B)   # 합집합   {1,2,3,4,5,6,7}
print(A & B)   # 교집합   {3,4,5}
print(A - B)   # 차집합   {1,2}
print(A ^ B)   # 대칭차집합 {1,2,6,7}

# 부분집합 / 초집합
print({1,2}.issubset(A))    # True
print(A.issuperset({1,2}))  # True
print(A.isdisjoint({8,9}))  # True (공통 원소 없음)

# frozenset (딕셔너리 키, 셋 원소로 사용 가능)
fs = frozenset([1,2,3])
```

---

## 🧪 LAB 1 – 이 repo의 hashtest.py 확장 (10:00 – 12:00)

```python
# day13_set_extended.py  (hashtest.py 기반 확장)

def set_demo():
    fruits = set()
    for f in ["Apple","Banana","Orange","Apple","Mango","Banana"]:
        fruits.add(f)

    print(f"중복 제거 결과 ({len(fruits)}개): {sorted(fruits)}")
    print(f"'Banana' 포함: {'Banana' in fruits}")

    fruits.discard("Orange")
    print(f"Orange 제거 후: {sorted(fruits)}")
    return fruits

def compare_sets(a: set, b: set) -> None:
    print(f"\nA = {sorted(a)}")
    print(f"B = {sorted(b)}")
    print(f"합집합  : {sorted(a | b)}")
    print(f"교집합  : {sorted(a & b)}")
    print(f"차집합A : {sorted(a - b)}")
    print(f"대칭차  : {sorted(a ^ b)}")

tropical  = {"Mango","Pineapple","Papaya","Banana"}
temperate = {"Apple","Pear","Grape","Banana","Cherry"}
compare_sets(tropical, temperate)
```

---

## 🧪 LAB 2 – 중복 제거 실용 패턴 (13:00 – 15:00)

```python
# day13_dedup.py

# 1. 리스트 중복 제거 (순서 유지)
def deduplicate_ordered(lst: list) -> list:
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

data = [3,1,4,1,5,9,2,6,5,3,5]
print("중복 제거(순서 유지):", deduplicate_ordered(data))
print("중복 제거(정렬):    ", sorted(set(data)))

# 2. 공통 태그 찾기
posts = [
    {"title":"Python 기초", "tags":{"python","programming","beginner"}},
    {"title":"FastAPI 튜토리얼", "tags":{"python","fastapi","api","web"}},
    {"title":"데이터 분석", "tags":{"python","pandas","data","beginner"}},
]

all_tags   = set().union(*[p["tags"] for p in posts])
common_all = set(posts[0]["tags"]).intersection(*[p["tags"] for p in posts])
print(f"\n전체 태그: {sorted(all_tags)}")
print(f"공통 태그: {sorted(common_all)}")

# 3. 두 파일 비교 (집합 활용)
file_a = {"a.py","b.py","c.py","d.py"}
file_b = {"b.py","c.py","e.py","f.py"}
print(f"\n두 폴더 모두 존재: {sorted(file_a & file_b)}")
print(f"A에만 존재:        {sorted(file_a - file_b)}")
print(f"B에만 존재:        {sorted(file_b - file_a)}")
```

---

## 🧪 LAB 3 – 추천 시스템 (15:00 – 17:00)

```python
# day13_recommend.py

users = {
    "alice": {"python","fastapi","docker","git"},
    "bob":   {"python","django","postgresql","docker"},
    "carol": {"javascript","react","node","docker"},
    "dave":  {"python","fastapi","kubernetes","docker"},
}

def recommend_connections(username: str, all_users: dict) -> list[tuple[str,float]]:
    """공통 관심사 기반 연결 추천"""
    my_tags = all_users[username]
    recommendations = []
    for other, tags in all_users.items():
        if other == username:
            continue
        common = len(my_tags & tags)
        total  = len(my_tags | tags)
        similarity = common / total  # Jaccard 유사도
        if common > 0:
            recommendations.append((other, similarity, sorted(my_tags & tags)))
    return sorted(recommendations, key=lambda x: x[1], reverse=True)

for user in users:
    recs = recommend_connections(user, users)
    print(f"\n{user}의 추천:")
    for other, sim, common in recs:
        print(f"  → {other} (유사도:{sim:.0%}, 공통:{common})")
```

---

## 📝 과제 (17:00 – 18:00)

`day13_homework.py` – 로또 시뮬레이터

1. `random.sample(range(1,46), 6)` 으로 당첨 번호 생성 (set)
2. 사용자 번호 6개 입력 (공백 구분)
3. 당첨 번호와 비교해 몇 개 일치하는지 계산
4. 등수 출력: 6개→1등, 5개→2등, 4개→3등, 3개→4등, 기타→꽝

---

## ✅ 체크리스트

- [ ] `add/update/remove/discard/pop` 메서드 활용
- [ ] 집합 연산 4종 (`|`, `&`, `-`, `^`) 완성
- [ ] `issubset/issuperset/isdisjoint` 이해
- [ ] 중복 제거 순서 유지 함수 완성
- [ ] Jaccard 유사도 추천 시스템 완성
- [ ] 로또 시뮬레이터 과제 완성
