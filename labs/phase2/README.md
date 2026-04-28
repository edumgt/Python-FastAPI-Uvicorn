# Phase 2 – 자료구조 & 객체지향(OOP) (Day 21 ~ 40)

> **기간**: Day 21 – 40 | **총 160시간**

---

## 📋 Phase 2 학습 로드맵

| Day | 주제 | 핵심 키워드 |
|-----|------|------------|
| 21 | 클래스 기초 | `class`, `__init__`, `self` |
| 22 | 인스턴스 vs 클래스 속성 | `@classmethod`, `@staticmethod` |
| 23 | 상속 | `super()`, MRO |
| 24 | 다형성 | 메서드 오버라이딩 |
| 25 | 캡슐화 | `@property`, `_`, `__` |
| 26 | 매직 메서드 | `__str__`, `__add__`, `__len__` |
| 27 | 추상 클래스 | `abc.ABC`, `@abstractmethod` |
| 28 | 스택 & 큐 | `list`, `collections.deque` |
| 29 | 연결 리스트 | `Node`, `LinkedList` |
| 30 | 정렬 알고리즘 | 버블·선택·삽입·퀵·병합 |
| 31 | 해시맵 심화 | `dict` 내부 원리, 충돌 |
| 32 | 재귀 | 메모이제이션, 꼬리 재귀 |
| 33 | 컴프리헨션 심화 | 중첩·제너레이터식 |
| 34 | 이터레이터 | `__iter__`, `__next__` |
| 35 | 제너레이터 | `yield`, `yield from` |
| 36 | 함수형 | `lambda`, `map`, `filter`, `reduce` |
| 37 | 정규표현식 | `re` 모듈, 패턴 |
| 38 | collections | `Counter`, `deque`, `defaultdict`, `OrderedDict` |
| 39 | 미니 프로젝트 | OOP 성적 관리 시스템 |
| 40 | Phase 2 리뷰 | 코드 리뷰·자기평가 |

---

# Day 21 – 클래스 기초

## 🎯 학습 목표

- `class` 정의, `__init__`, `self` 완전 이해
- 인스턴스 생성 및 속성 접근
- 인스턴스 메서드 작성

## 📖 이론 (08:00 – 10:00)

```python
class BankAccount:
    """은행 계좌 클래스"""

    bank_name = "파이썬 은행"          # 클래스 변수 (모든 인스턴스 공유)

    def __init__(self, owner: str, balance: float = 0.0):
        self.owner   = owner           # 인스턴스 변수
        self.balance = balance
        self._history: list[str] = []  # 내부용 (관례적 private)

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("입금액은 양수여야 합니다")
        self.balance += amount
        self._history.append(f"+{amount:,.0f}원")

    def withdraw(self, amount: float) -> None:
        if amount > self.balance:
            raise ValueError("잔액 부족")
        self.balance -= amount
        self._history.append(f"-{amount:,.0f}원")

    def get_history(self) -> list[str]:
        return self._history.copy()

    def __str__(self) -> str:
        return f"[{self.bank_name}] {self.owner}: {self.balance:,.0f}원"

# 사용
acc1 = BankAccount("홍길동", 10000)
acc2 = BankAccount("김철수")

acc1.deposit(5000)
acc1.withdraw(3000)
print(acc1)                          # [파이썬 은행] 홍길동: 12,000원
print(acc1.get_history())
print(BankAccount.bank_name)         # 클래스 변수 접근
```

## 🧪 LAB 1 – Student 클래스 (10:00 – 12:00)

```python
# day21_student.py

class Student:
    school = "파이썬 고등학교"

    def __init__(self, name: str, grade: int, scores: dict[str, int]):
        self.name   = name
        self.grade  = grade
        self.scores = scores   # {"국어":85, "영어":92, "수학":78}

    def average(self) -> float:
        return sum(self.scores.values()) / len(self.scores)

    def highest_subject(self) -> str:
        return max(self.scores, key=self.scores.get)

    def report(self) -> str:
        lines = [f"=== {self.name} ({self.grade}학년) ==="]
        for subj, score in self.scores.items():
            lines.append(f"  {subj}: {score}점")
        lines.append(f"  평균: {self.average():.1f}점")
        lines.append(f"  최고: {self.highest_subject()}")
        return "\n".join(lines)

students = [
    Student("홍길동", 1, {"국어":85,"영어":92,"수학":78}),
    Student("김철수", 2, {"국어":91,"영어":88,"수학":95}),
    Student("이영희", 1, {"국어":79,"영어":84,"수학":91}),
]

for s in students:
    print(s.report())
    print()

# 학년 1 평균
grade1 = [s for s in students if s.grade == 1]
class_avg = sum(s.average() for s in grade1) / len(grade1)
print(f"1학년 평균: {class_avg:.1f}점")
```

## 🧪 LAB 2 – Vector 클래스 (13:00 – 15:00)

```python
# day21_vector.py
import math

class Vector2D:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def magnitude(self) -> float:
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self) -> "Vector2D":
        mag = self.magnitude()
        if mag == 0:
            raise ValueError("영벡터는 정규화 불가")
        return Vector2D(self.x / mag, self.y / mag)

    def dot(self, other: "Vector2D") -> float:
        return self.x * other.x + self.y * other.y

    def angle_between(self, other: "Vector2D") -> float:
        cos_theta = self.dot(other) / (self.magnitude() * other.magnitude())
        return math.degrees(math.acos(max(-1, min(1, cos_theta))))

    def __add__(self, other: "Vector2D") -> "Vector2D":
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector2D") -> "Vector2D":
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vector2D":
        return Vector2D(self.x * scalar, self.y * scalar)

    def __repr__(self) -> str:
        return f"Vector2D({self.x:.2f}, {self.y:.2f})"

v1 = Vector2D(3, 4)
v2 = Vector2D(1, 0)
print(f"|v1| = {v1.magnitude()}")
print(f"v1 + v2 = {v1 + v2}")
print(f"v1 · v2 = {v1.dot(v2)}")
print(f"v1과 v2 각도 = {v1.angle_between(v2):.1f}°")
```

## 🧪 LAB 3 – 도전: 도서 클래스 (15:00 – 17:00)

`Book`, `Library` 클래스를 구현하세요.
- `Book`: isbn, title, author, year, available(대출 여부)
- `Library`: books 목록, add/borrow/return/search 메서드

## 📝 과제 (17:00 – 18:00)

`day21_homework.py` – `Playlist` 클래스

- 노래(제목, 아티스트, 길이(초)) 추가/제거
- 전체 재생 시간, 랜덤 셔플, 특정 아티스트 노래 필터링

---

# Day 22 – 인스턴스 vs 클래스 속성

## 🎯 학습 목표

- `@classmethod` vs `@staticmethod` vs 인스턴스 메서드 구분
- 클래스 변수 공유 메커니즘 이해
- 대안 생성자 패턴 (Alternative Constructor)

## 📖 이론 (08:00 – 10:00)

```python
from datetime import date

class Person:
    count = 0   # 클래스 변수

    def __init__(self, name: str, birth_year: int):
        self.name       = name
        self.birth_year = birth_year
        Person.count   += 1

    @classmethod
    def from_birth_date(cls, name: str, birth_date: str) -> "Person":
        """대안 생성자: 'YYYY-MM-DD' 형식 날짜 문자열로 생성"""
        year = int(birth_date.split("-")[0])
        return cls(name, year)

    @staticmethod
    def is_valid_year(year: int) -> bool:
        """정적 메서드: self/cls 불필요한 유틸리티"""
        return 1900 <= year <= date.today().year

    @property
    def age(self) -> int:
        return date.today().year - self.birth_year

    @classmethod
    def get_count(cls) -> int:
        return cls.count

p1 = Person("홍길동", 1990)
p2 = Person.from_birth_date("김철수", "1995-06-15")
print(p1.age, p2.age)
print(Person.get_count())           # 2
print(Person.is_valid_year(2030))   # False
```

## 🧪 LAB 실습 (10:00 – 17:00)

```python
# day22_class_methods.py

class Temperature:
    """온도 클래스 – 내부적으로 켈빈(K) 저장"""

    ABSOLUTE_ZERO = -273.15  # 클래스 상수

    def __init__(self, kelvin: float):
        if kelvin < 0:
            raise ValueError("켈빈은 0 이상이어야 합니다")
        self._kelvin = kelvin

    @classmethod
    def from_celsius(cls, c: float) -> "Temperature":
        return cls(c + 273.15)

    @classmethod
    def from_fahrenheit(cls, f: float) -> "Temperature":
        return cls((f - 32) * 5/9 + 273.15)

    @staticmethod
    def celsius_to_fahrenheit(c: float) -> float:
        return c * 9/5 + 32

    @property
    def kelvin(self) -> float:    return self._kelvin
    @property
    def celsius(self) -> float:   return self._kelvin - 273.15
    @property
    def fahrenheit(self) -> float: return self.celsius * 9/5 + 32

    def __str__(self) -> str:
        return (f"{self.kelvin:.2f}K / "
                f"{self.celsius:.2f}°C / "
                f"{self.fahrenheit:.2f}°F")

temps = [
    Temperature.from_celsius(0),
    Temperature.from_celsius(100),
    Temperature.from_fahrenheit(32),
    Temperature.from_fahrenheit(212),
]
for t in temps:
    print(t)
```

---

# Day 23 – 상속

## 🎯 학습 목표

- 단일 상속, 다중 상속, `super()` 활용
- MRO(Method Resolution Order) 이해
- `isinstance()`, `issubclass()` 활용

## 📖 이론 & LAB (08:00 – 17:00)

```python
# day23_inheritance.py

class Animal:
    def __init__(self, name: str, sound: str):
        self.name  = name
        self.sound = sound

    def speak(self) -> str:
        return f"{self.name}: {self.sound}!"

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.name!r})"

class Dog(Animal):
    def __init__(self, name: str, breed: str):
        super().__init__(name, "멍멍")
        self.breed = breed

    def fetch(self) -> str:
        return f"{self.name}이(가) 공을 물어왔습니다!"

class GuideDog(Dog):
    def __init__(self, name: str, breed: str, owner: str):
        super().__init__(name, breed)
        self.owner = owner

    def guide(self) -> str:
        return f"{self.name}이(가) {self.owner}을(를) 안내합니다."

class Cat(Animal):
    def __init__(self, name: str):
        super().__init__(name, "야옹")

    def purr(self) -> str:
        return f"{self.name}: 그루릉..."

# MRO 확인
print(GuideDog.__mro__)

animals = [Dog("바둑이","진도"), Cat("나비"), GuideDog("별이","래브라도","홍길동")]
for a in animals:
    print(a.speak())
    if isinstance(a, Dog):
        print(f"  → {a.fetch()}")
    if isinstance(a, GuideDog):
        print(f"  → {a.guide()}")
```

---

# Day 39 – 미니 프로젝트: OOP 성적 관리 시스템

## 프로젝트 구조

```
grade_system/
├── __init__.py
├── models.py     # Student, Subject, Grade 클래스
├── manager.py    # GradeManager (CRUD)
├── report.py     # 통계·리포트 생성
├── storage.py    # JSON 저장소
└── main.py       # CLI 진입점
```

## 요구사항

- 학생 등록/수정/삭제
- 과목별 점수 입력 (최대 100점)
- 학생별·과목별 통계 (평균, 최고, 최저, 표준편차)
- 석차 계산 (동점자 처리 포함)
- 성적표 텍스트 파일 출력

```python
# 핵심 모델 예시 (day39 전체 구현)
from dataclasses import dataclass, field

@dataclass
class Grade:
    subject: str
    score:   float

    @property
    def letter(self) -> str:
        if self.score >= 95: return "A+"
        elif self.score >= 90: return "A"
        elif self.score >= 85: return "B+"
        elif self.score >= 80: return "B"
        elif self.score >= 75: return "C+"
        elif self.score >= 70: return "C"
        elif self.score >= 60: return "D"
        else:                  return "F"

@dataclass
class Student:
    id:     int
    name:   str
    grades: list[Grade] = field(default_factory=list)

    def add_grade(self, subject: str, score: float) -> None:
        self.grades = [g for g in self.grades if g.subject != subject]
        self.grades.append(Grade(subject, score))

    def average(self) -> float:
        if not self.grades: return 0.0
        return sum(g.score for g in self.grades) / len(self.grades)

    def gpa(self) -> float:
        """4.5 만점 환산 GPA"""
        avg = self.average()
        if avg >= 95: return 4.5
        elif avg >= 90: return 4.0
        elif avg >= 85: return 3.5
        elif avg >= 80: return 3.0
        elif avg >= 75: return 2.5
        elif avg >= 70: return 2.0
        elif avg >= 60: return 1.0
        else:           return 0.0
```

---

# Day 40 – Phase 2 종합 리뷰

## 🧪 Phase 2 핵심 패턴 총정리

```python
# 1. 추상 클래스 + 상속 + 다형성
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...

    @abstractmethod
    def perimeter(self) -> float: ...

    def describe(self) -> str:
        return (f"{type(self).__name__}: "
                f"넓이={self.area():.2f}, 둘레={self.perimeter():.2f}")

class Circle(Shape):
    def __init__(self, r): self.r = r
    def area(self): return 3.14159 * self.r ** 2
    def perimeter(self): return 2 * 3.14159 * self.r

class Rectangle(Shape):
    def __init__(self, w, h): self.w, self.h = w, h
    def area(self): return self.w * self.h
    def perimeter(self): return 2 * (self.w + self.h)

shapes: list[Shape] = [Circle(5), Rectangle(4,6), Circle(3)]
for s in shapes:
    print(s.describe())

# 정렬 (다형성 활용)
shapes.sort(key=lambda s: s.area())
print("\n넓이 순:", [type(s).__name__ for s in shapes])

# 2. 이터레이터 직접 구현
class CountDown:
    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        val = self.current
        self.current -= 1
        return val

print(list(CountDown(5)))  # [5,4,3,2,1]

# 3. 제너레이터
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

gen = fibonacci()
print([next(gen) for _ in range(10)])  # [0,1,1,2,3,5,8,13,21,34]
```

## 자기 평가 테스트

| 개념 | 자신감 (1-5) |
|------|-------------|
| 클래스/인스턴스 변수 구분 | /5 |
| @classmethod / @staticmethod | /5 |
| 상속 & MRO | /5 |
| 다형성 / 추상 클래스 | /5 |
| @property 캡슐화 | /5 |
| 매직 메서드 | /5 |
| 이터레이터 / 제너레이터 | /5 |
| 재귀 & 메모이제이션 | /5 |
| **총점** | **/40** |
