# Day 11 – 튜플과 언패킹

> **소요시간**: 8시간 | **Phase**: 1 – Python 완전 기초

---

## 🎯 학습 목표

- 튜플(tuple)의 불변성 특성 이해
- 튜플 패킹 & 언패킹, `*` 연산자 활용
- `namedtuple` 로 가독성 있는 튜플 사용
- 함수 다중 반환값과 튜플의 관계

---

## 📖 이론 (08:00 – 10:00)

```python
# 생성
t1 = (1, 2, 3)
t2 = 1, 2, 3        # 괄호 생략 가능 (패킹)
t3 = (42,)          # 단일 요소: 쉼표 필수!
t4 = tuple([1,2,3]) # 리스트 → 튜플

# 불변성
# t1[0] = 99   # TypeError!

# 기본 연산
print(len(t1))              # 3
print(t1 + (4, 5))          # (1,2,3,4,5)
print(t1 * 2)               # (1,2,3,1,2,3)
print(2 in t1)              # True

# 언패킹
a, b, c = t1
first, *rest = (1,2,3,4,5)  # first=1, rest=[2,3,4,5]
*init, last  = (1,2,3,4,5)  # init=[1,2,3,4], last=5

# namedtuple
from collections import namedtuple
Point = namedtuple("Point", ["x", "y"])
p = Point(3, 4)
print(p.x, p.y)             # 3 4
print(p._asdict())           # OrderedDict
```

---

## 🧪 LAB 1 – 언패킹 실습 (10:00 – 12:00)

```python
# day11_unpack.py

# 좌표 데이터 처리
def distance(p1: tuple, p2: tuple) -> float:
    x1, y1 = p1
    x2, y2 = p2
    return ((x2-x1)**2 + (y2-y1)**2) ** 0.5

points = [(0,0),(3,0),(3,4),(0,4)]
for i in range(len(points)):
    j = (i+1) % len(points)
    d = distance(points[i], points[j])
    print(f"  {points[i]} → {points[j]}: {d:.2f}")

# * 언패킹 활용
first, second, *middle, last = range(10)
print(f"first={first}, second={second}, middle={middle}, last={last}")

# 스왑 (임시 변수 불필요)
a, b = 10, 20
a, b = b, a
print(f"a={a}, b={b}")  # a=20, b=10
```

---

## 🧪 LAB 2 – namedtuple 활용 (13:00 – 15:00)

```python
# day11_namedtuple.py
from collections import namedtuple

Student = namedtuple("Student", ["name", "age", "score", "grade"])

students_data = [
    ("홍길동", 20, 85, "B"),
    ("김철수", 22, 92, "A"),
    ("이영희", 21, 78, "C"),
    ("박민준", 23, 96, "A+"),
]
students = [Student(*d) for d in students_data]

# 이름순 정렬
for s in sorted(students, key=lambda s: s.name):
    print(f"  {s.name} ({s.age}세) | {s.score}점 | {s.grade}")

# A학점 이상 학생
a_students = [s for s in students if "A" in s.grade]
print(f"\nA학점 이상: {[s.name for s in a_students]}")
print(f"평균 점수 : {sum(s.score for s in students)/len(students):.1f}")
```

---

## 🧪 LAB 3 – 튜플 vs 리스트 벤치마크 (15:00 – 17:00)

```python
# day11_benchmark.py
import timeit

# 생성 속도 비교
list_time  = timeit.timeit("[1,2,3,4,5,6,7,8,9,10]", number=1_000_000)
tuple_time = timeit.timeit("(1,2,3,4,5,6,7,8,9,10)", number=1_000_000)

print(f"리스트 생성 100만회: {list_time:.4f}초")
print(f"튜플  생성 100만회: {tuple_time:.4f}초")
print(f"튜플이 {list_time/tuple_time:.1f}배 빠름")

# 튜플을 딕셔너리 키로 사용
grid = {}
for row in range(3):
    for col in range(3):
        grid[(row, col)] = row * 3 + col + 1

print("\n=== 체스판 좌표 맵 ===")
for (r, c), val in sorted(grid.items()):
    print(f"  ({r},{c}) → {val}")
```

---

## 📝 과제 (17:00 – 18:00)

`day11_homework.py` – RGB 색상 변환기

1. `Color = namedtuple("Color", ["r", "g", "b", "name"])` 정의
2. 5가지 색 데이터 정의
3. RGB → HEX 변환 함수 구현: `(255,0,0)` → `"#FF0000"`
4. 밝기 순 정렬: 밝기 = `0.299*r + 0.587*g + 0.114*b`

---

## ✅ 체크리스트

- [ ] 튜플 불변성 및 단일 요소 튜플 이해
- [ ] `*` 언패킹 모든 패턴 실습
- [ ] 좌표 거리 계산 완성
- [ ] `namedtuple` 학생 데이터 처리 완성
- [ ] 튜플 vs 리스트 성능 비교 완성
- [ ] RGB 색상 변환기 과제 완성
