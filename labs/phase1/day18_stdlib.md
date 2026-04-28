# Day 18 – 표준 라이브러리 (os, sys, pathlib, datetime)

> **소요시간**: 8시간 | **Phase**: 1 – Python 완전 기초

---

## 🎯 학습 목표

- `os` / `os.path` 로 파일시스템 조작
- `pathlib.Path` 객체지향 경로 처리
- `datetime` 날짜·시간 연산
- `sys` 모듈로 런타임 정보 조회

---

## 📖 이론 (08:00 – 10:00)

```python
import os
from pathlib import Path
from datetime import date, time, datetime, timedelta
import sys

# os 모듈
print(os.getcwd())                  # 현재 경로
os.makedirs("tmp/sub", exist_ok=True)
os.listdir(".")                     # 파일 목록
os.path.exists("users.json")        # 존재 여부
os.path.join("data","file.txt")     # 경로 결합

# pathlib (권장)
p = Path(".")
for f in p.glob("*.py"):            # Python 파일 목록
    print(f.name, f.stat().st_size)

# datetime
now  = datetime.now()
today = date.today()
print(now.strftime("%Y-%m-%d %H:%M:%S"))
print(today.isoformat())

delta = timedelta(days=30)
print(today + delta)                # 30일 후
diff  = datetime(2026, 12, 31) - datetime.now()
print(f"연말까지 {diff.days}일")

# sys
print(sys.version)
print(sys.platform)
print(sys.argv)                     # 커맨드라인 인자
```

---

## 🧪 LAB 1 – 파일시스템 탐색기 (10:00 – 12:00)

```python
# day18_explorer.py
from pathlib import Path
import os

def explore(root: Path, indent: int = 0) -> None:
    """디렉터리 트리를 재귀적으로 출력"""
    prefix = "  " * indent
    print(f"{prefix}📁 {root.name}/")
    try:
        for child in sorted(root.iterdir()):
            if child.name.startswith("."):
                continue
            if child.is_dir():
                explore(child, indent + 1)
            else:
                size = child.stat().st_size
                print(f"{prefix}  📄 {child.name} ({size:,} bytes)")
    except PermissionError:
        print(f"{prefix}  🔒 접근 거부")

def get_stats(root: Path) -> dict:
    """디렉터리 파일 통계"""
    stats = {"total_files": 0, "total_dirs": 0,
             "total_size": 0, "by_ext": {}}
    for item in root.rglob("*"):
        if item.is_file():
            stats["total_files"] += 1
            stats["total_size"] += item.stat().st_size
            ext = item.suffix or "(없음)"
            stats["by_ext"][ext] = stats["by_ext"].get(ext, 0) + 1
        elif item.is_dir():
            stats["total_dirs"] += 1
    return stats

root = Path(".")
stats = get_stats(root)
print(f"파일: {stats['total_files']}개, 폴더: {stats['total_dirs']}개")
print(f"총 크기: {stats['total_size']:,} bytes")
print("확장자별:", dict(sorted(stats["by_ext"].items())))
```

---

## 🧪 LAB 2 – datetime 달력 (13:00 – 15:00)

```python
# day18_calendar.py
from datetime import date, timedelta
import calendar

def print_month(year: int, month: int) -> None:
    """월별 달력 출력"""
    cal = calendar.monthcalendar(year, month)
    month_name = date(year, month, 1).strftime("%B %Y")
    print(f"\n    {'─'*18}")
    print(f"    {month_name:^18}")
    print(f"    {'─'*18}")
    print(f"    {'월 화 수 목 금 토 일':18}")
    for week in cal:
        row = ""
        for day in week:
            row += f"{'':3}" if day == 0 else f"{day:3}"
        print(f"   {row}")
    print(f"    {'─'*18}")

def days_until(target: date) -> int:
    return (target - date.today()).days

def age_calculator(birth_year: int, birth_month: int, birth_day: int) -> dict:
    birth = date(birth_year, birth_month, birth_day)
    today = date.today()
    age   = today.year - birth.year - (
        (today.month, today.day) < (birth.month, birth.day)
    )
    next_bday = date(today.year, birth.month, birth.day)
    if next_bday < today:
        next_bday = date(today.year+1, birth.month, birth.day)
    return {"age": age, "days_alive": (today - birth).days,
            "next_birthday_in": (next_bday - today).days}

print_month(2026, 4)
print_month(2026, 12)

info = age_calculator(2000, 3, 15)
print(f"\n나이: {info['age']}세 | 살아온 날: {info['days_alive']:,}일 | "
      f"다음 생일까지: {info['next_birthday_in']}일")
```

---

## 🧪 LAB 3 – sys 커맨드라인 인자 처리 (15:00 – 17:00)

```python
# day18_cli.py
"""
사용법:
  python day18_cli.py stats <경로>      # 파일 통계
  python day18_cli.py find <경로> <확장자>  # 파일 검색
  python day18_cli.py info              # 시스템 정보
"""
import sys
from pathlib import Path
import platform
from datetime import datetime

def cmd_stats(path: str) -> None:
    p = Path(path)
    if not p.exists():
        print(f"오류: '{path}' 가 존재하지 않습니다"); return
    if p.is_file():
        stat = p.stat()
        print(f"파일: {p.name}")
        print(f"크기: {stat.st_size:,} bytes")
        print(f"수정: {datetime.fromtimestamp(stat.st_mtime):%Y-%m-%d %H:%M}")
    else:
        files = list(p.rglob("*"))
        print(f"폴더: {p.name} | 항목 수: {len(files)}개")

def cmd_find(path: str, ext: str) -> None:
    ext = ext if ext.startswith(".") else "." + ext
    found = list(Path(path).rglob(f"*{ext}"))
    print(f"'{ext}' 파일 {len(found)}개 발견:")
    for f in found[:10]:
        print(f"  {f}")

def cmd_info() -> None:
    print(f"Python: {sys.version}")
    print(f"OS    : {platform.system()} {platform.release()}")
    print(f"현재  : {Path.cwd()}")

args = sys.argv[1:]
if not args or args[0] == "info":
    cmd_info()
elif args[0] == "stats" and len(args) >= 2:
    cmd_stats(args[1])
elif args[0] == "find" and len(args) >= 3:
    cmd_find(args[1], args[2])
else:
    print(__doc__)
```

---

## 📝 과제 (17:00 – 18:00)

`day18_homework.py` – 파일 백업 유틸리티

1. `backup(src_dir, dst_dir)` 함수:
   - `src_dir` 의 모든 `.py` 파일을 `dst_dir`에 복사
   - 파일명에 `_YYYYMMDD_HHMMSS` 타임스탬프 추가
2. `clean_old_backups(dst_dir, keep_days=7)`:
   - `dst_dir`에서 7일 이상 된 백업 파일 삭제
3. `sys.argv`로 경로 입력 받기

---

## ✅ 체크리스트

- [ ] `os.makedirs`, `os.listdir`, `os.path.exists` 활용
- [ ] `pathlib.Path` 로 glob/rglob 완성
- [ ] 파일시스템 탐색기 완성
- [ ] 달력 및 생일 계산 완성
- [ ] `sys.argv` CLI 도구 완성
- [ ] 파일 백업 유틸리티 과제 완성
