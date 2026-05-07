# Day 17 – 모듈 & 패키지

> **소요시간**: 8시간 | **Phase**: 1 – Python 완전 기초

---

## 🎯 학습 목표

- `import`, `from ... import`, `as` 키워드 이해
- 패키지 구조 (`__init__.py`) 설계
- `if __name__ == "__main__"` 관용구 이해
- 이 repo의 모듈 분리 패턴 (`mydata.py`, `hashtest.py`) 분석

---

## 📖 이론 (08:00 – 10:00)

```python
# import 방식 4가지
import math                        # 1) 모듈 전체
from math import sqrt, pi         # 2) 특정 함수
from math import *                 # 3) 전체 (비권장)
import numpy as np                 # 4) 별칭

# __name__ 관용구
# 파일이 직접 실행될 때만 main() 호출
# 다른 모듈에서 import 될 때는 실행되지 않음
def main():
    print("직접 실행됨")

if __name__ == "__main__":
    main()
```

### 패키지 구조 예시

```
myapp/
├── __init__.py          # 패키지 초기화
├── utils/
│   ├── __init__.py
│   ├── string_utils.py
│   └── math_utils.py
├── models/
│   ├── __init__.py
│   └── user.py
└── main.py
```

---

## 🧪 LAB 1 – 이 repo 모듈 분석 (10:00 – 12:00)

`app.py`, `mydata.py`, `hashtest.py`, `logintest.py` 의 모듈 분리 패턴을 분석하고 확장하세요.

```python
# day17_module_analysis.py

# 이 repo의 모듈 구조 재현
# mydata.py   → get_data() 함수 제공
# hashtest.py → get_fruits_info() 함수 제공
# app.py      → 두 모듈 import 후 FastAPI 라우터에 연결

# 새 모듈: stats.py 를 만들어 app.py에 추가하는 시뮬레이션
def get_stats():
    """통계 데이터 반환"""
    return {
        "total_users": 42,
        "active_users": 38,
        "requests_today": 1523,
    }

# 모듈을 함수처럼 사용
import importlib, sys

# sys.path 확인
print("Python 경로 (처음 3개):")
for p in sys.path[:3]:
    print(f"  {p}")

# 모듈 정보 확인
import math
print(f"\nmath 모듈 위치: {math.__file__}")
print(f"math 모듈 속성: {[a for a in dir(math) if not a.startswith('_')][:10]}")
```

---

## 🧪 LAB 2 – 패키지 만들기 (13:00 – 15:00)

아래 패키지 구조를 직접 만들고 테스트하세요.

```
utils/
├── __init__.py
├── string_utils.py
├── math_utils.py
└── file_utils.py
```

```python
# utils/__init__.py
from .string_utils import (clean_text, to_snake_case)
from .math_utils   import (clamp, lerp)
from .file_utils   import (safe_read, safe_write)

__all__ = ["clean_text","to_snake_case","clamp","lerp","safe_read","safe_write"]
__version__ = "0.1.0"
```

```python
# utils/string_utils.py
import re

def clean_text(text: str) -> str:
    """공백 정규화 및 특수문자 제거"""
    text = re.sub(r'\s+', ' ', text).strip()
    return re.sub(r'[^\w\s가-힣]', '', text)

def to_snake_case(text: str) -> str:
    """CamelCase → snake_case"""
    text = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', text)
    text = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', text)
    return text.lower()
```

```python
# utils/math_utils.py
def clamp(value: float, min_val: float, max_val: float) -> float:
    """값을 [min_val, max_val] 범위로 제한"""
    return max(min_val, min(max_val, value))

def lerp(a: float, b: float, t: float) -> float:
    """선형 보간: t=0이면 a, t=1이면 b"""
    return a + (b - a) * clamp(t, 0.0, 1.0)
```

```python
# utils/file_utils.py
from pathlib import Path
import json

def safe_read(path: str | Path, default=None):
    try:
        p = Path(path)
        if p.suffix == ".json":
            return json.loads(p.read_text(encoding="utf-8"))
        return p.read_text(encoding="utf-8")
    except (FileNotFoundError, json.JSONDecodeError):
        return default

def safe_write(path: str | Path, data) -> bool:
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(data, (dict, list)):
            p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        else:
            p.write_text(str(data), encoding="utf-8")
        return True
    except OSError:
        return False
```

```python
# day17_test_package.py
from utils import clean_text, to_snake_case, clamp, lerp, safe_read, safe_write
import utils

print(utils.__version__)
print(clean_text("  Hello,  World!  🎉  "))
print(to_snake_case("MyFastAPIApp"))
print(clamp(150, 0, 100))
print(lerp(0, 100, 0.25))
print(safe_read("users.json"))
```

---

## 🧪 LAB 3 – 표준 라이브러리 탐구 (15:00 – 17:00)

```python
# day17_stdlib.py
import random, math, statistics, itertools, functools

# random
nums = [random.randint(1,100) for _ in range(20)]
print("랜덤 리스트:", nums)
random.shuffle(nums)
print("셔플 후:", nums[:5], "...")
print("선택:", random.choice(nums))
print("샘플 3개:", random.sample(nums, 3))

# statistics
print(f"\n평균  : {statistics.mean(nums):.1f}")
print(f"중앙값: {statistics.median(nums):.1f}")
print(f"표준편차: {statistics.stdev(nums):.2f}")

# itertools
from itertools import permutations, combinations, product
letters = ['A','B','C']
print("\n순열 3개:", list(permutations(letters)))
print("조합 2개:", list(combinations(letters,2)))
print("곱집합:", list(product([0,1],[0,1])))

# functools.lru_cache
@functools.lru_cache(maxsize=128)
def fib(n: int) -> int:
    return n if n < 2 else fib(n-1) + fib(n-2)

print("\nfib(30):", fib(30))
print("캐시 정보:", fib.cache_info())
```

---

## 📝 과제 (17:00 – 18:00)

`day17_homework/` 패키지를 만드세요.

```
day17_homework/
├── __init__.py
├── validators.py     # is_email(), is_phone(), is_url()
├── formatters.py     # format_phone(), format_money(), format_date()
└── test_homework.py  # 각 함수 테스트
```

---

## ✅ 체크리스트

- [ ] `import` 4가지 방식 모두 사용
- [ ] `if __name__ == "__main__"` 이해
- [ ] 이 repo 모듈 분리 패턴 분석
- [ ] `utils/` 패키지 4파일 완성
- [ ] 표준 라이브러리 random/statistics/itertools 실습
- [ ] `day17_homework/` 패키지 과제 완성

🔎 유튜브 관련 영상 검색: https://www.youtube.com/results?search_query=python+trading+day17+modules
