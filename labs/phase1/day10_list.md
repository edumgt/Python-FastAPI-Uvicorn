# Day 10 – 리스트

> **소요시간**: 8시간 | **Phase**: 1 – Python 완전 기초

---

## 🎯 학습 목표

- 리스트 생성·CRUD 전체 메서드 숙달
- 리스트 컴프리헨션 (List Comprehension)
- 2차원(중첩) 리스트 처리
- `sorted()` vs `.sort()`, `key` 함수 활용

---

## 📖 이론 (08:00 – 10:00)

```python
# 생성
nums = [1, 2, 3, 4, 5]
mixed = [1, "hello", True, None, [1, 2]]

# CRUD
nums.append(6)          # 끝에 추가
nums.insert(0, 0)       # 인덱스 위치에 삽입
nums.extend([7, 8, 9])  # 여러 요소 추가
nums.remove(5)          # 값으로 제거 (첫 번째만)
popped = nums.pop()     # 마지막 제거 및 반환
popped = nums.pop(0)    # 인덱스로 제거
del nums[0]             # del 로 제거
nums.clear()            # 전체 제거

# 조회
idx = nums.index(3)     # 인덱스 반환
cnt = nums.count(3)     # 등장 횟수

# 정렬
nums.sort()                          # 오름차순 in-place
nums.sort(reverse=True)              # 내림차순 in-place
sorted_nums = sorted(nums)           # 새 리스트 반환
names = ["banana","apple","cherry"]
names.sort(key=lambda x: len(x))     # 길이 기준 정렬

# 리스트 컴프리헨션
squares = [x**2 for x in range(10)]
evens   = [x for x in range(20) if x % 2 == 0]
matrix  = [[i*j for j in range(1,4)] for i in range(1,4)]
```

---

## 🧪 LAB 1 – 리스트 CRUD 실습 (10:00 – 12:00)

```python
# day10_list_crud.py

# 할 일 목록 관리 (CRUD)
todos = []

def add_todo(task: str) -> None:
    todos.append({"id": len(todos)+1, "task": task, "done": False})

def complete_todo(task_id: int) -> bool:
    for todo in todos:
        if todo["id"] == task_id:
            todo["done"] = True
            return True
    return False

def delete_todo(task_id: int) -> bool:
    for i, todo in enumerate(todos):
        if todo["id"] == task_id:
            todos.pop(i)
            return True
    return False

def show_todos() -> None:
    for t in todos:
        status = "✅" if t["done"] else "⬜"
        print(f"  [{t['id']}] {status} {t['task']}")

# 테스트
add_todo("Python 공부")
add_todo("운동하기")
add_todo("장보기")
add_todo("독서")

print("=== 전체 목록 ==="); show_todos()
complete_todo(2)
print("\n=== 운동 완료 후 ==="); show_todos()
delete_todo(3)
print("\n=== 장보기 삭제 후 ==="); show_todos()
```

---

## 🧪 LAB 2 – 컴프리헨션 & 정렬 (13:00 – 15:00)

```python
# day10_comprehension.py

students = [
    {"name": "홍길동", "score": 85},
    {"name": "김철수", "score": 92},
    {"name": "이영희", "score": 78},
    {"name": "박민준", "score": 95},
    {"name": "최수진", "score": 88},
]

# 80점 이상 학생 이름 목록
passed = [s["name"] for s in students if s["score"] >= 80]
print("합격:", passed)

# 점수 내림차순 정렬
ranked = sorted(students, key=lambda s: s["score"], reverse=True)
print("\n=== 성적 순위 ===")
for rank, s in enumerate(ranked, 1):
    print(f"{rank}위. {s['name']}: {s['score']}점")

# 점수 20% 보정 후 새 리스트
boosted = [{"name": s["name"], "score": min(100, round(s["score"]*1.2))}
           for s in students]
print("\n=== 보정 후 점수 ===")
for s in boosted:
    print(f"  {s['name']}: {s['score']}점")
```

---

## 🧪 LAB 3 – 2차원 리스트: 행렬 연산 (15:00 – 17:00)

```python
# day10_matrix.py

def print_matrix(m, title=""):
    if title: print(f"\n{title}")
    for row in m:
        print(" ".join(f"{v:4d}" for v in row))

A = [[1,2,3],[4,5,6],[7,8,9]]
B = [[9,8,7],[6,5,4],[3,2,1]]

# 행렬 합
C_add = [[A[i][j] + B[i][j] for j in range(3)] for i in range(3)]

# 행렬 곱 (3×3)
def mat_mul(X, Y):
    n = len(X)
    return [[sum(X[i][k]*Y[k][j] for k in range(n)) for j in range(n)] for i in range(n)]

C_mul = mat_mul(A, B)

# 전치행렬
def transpose(M):
    return [[M[j][i] for j in range(len(M))] for i in range(len(M[0]))]

print_matrix(A, "행렬 A")
print_matrix(B, "행렬 B")
print_matrix(C_add, "A + B")
print_matrix(C_mul, "A × B")
print_matrix(transpose(A), "A의 전치")
```

---

## 📝 과제 (17:00 – 18:00)

`day10_homework.py` – 성적표 생성기

학생 10명의 이름과 3과목(국어/영어/수학) 점수를 리스트로 정의하고:
1. 각 학생의 총점과 평균 계산
2. 총점 기준 내림차순 정렬
3. 순위·이름·각 과목 점수·총점·평균을 표 형식으로 출력

---

## ✅ 체크리스트

- [ ] 리스트 CRUD 메서드 전부 사용
- [ ] 할 일 목록 CRUD 완성
- [ ] 컴프리헨션 + 조건 필터 활용
- [ ] `sorted()` + `key` 정렬 완성
- [ ] 2차원 리스트 행렬 연산 완성
- [ ] 성적표 생성기 과제 완성
