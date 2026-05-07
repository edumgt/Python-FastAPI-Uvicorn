# Day 14 – 파일 입출력

> **소요시간**: 8시간 | **Phase**: 1 – Python 완전 기초

---

## 🎯 학습 목표

- `open()` 함수 모드(`r/w/a/rb/wb`) 완전 이해
- `with` 문으로 안전한 파일 처리
- 텍스트 파일 읽기·쓰기·추가
- 바이너리 파일 및 `pathlib` 활용

---

## 📖 이론 (08:00 – 10:00)

```python
# 쓰기
with open("sample.txt", "w", encoding="utf-8") as f:
    f.write("첫 번째 줄\n")
    f.writelines(["두 번째\n", "세 번째\n"])

# 읽기 방법 3가지
with open("sample.txt", "r", encoding="utf-8") as f:
    content = f.read()         # 전체 문자열

with open("sample.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()      # 줄 단위 리스트

with open("sample.txt", "r", encoding="utf-8") as f:
    for line in f:             # 한 줄씩 (메모리 효율)
        print(line.strip())

# 추가 모드
with open("sample.txt", "a", encoding="utf-8") as f:
    f.write("추가된 줄\n")

# pathlib (권장)
from pathlib import Path

p = Path("data") / "sample.txt"
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text("pathlib으로 쓰기\n", encoding="utf-8")
print(p.read_text(encoding="utf-8"))
print(p.exists(), p.stat().st_size)
```

---

## 🧪 LAB 1 – 일기 앱 (10:00 – 12:00)

```python
# day14_diary.py
from pathlib import Path
from datetime import date

DIARY_FILE = Path("diary.txt")

def write_diary(content: str) -> None:
    today = date.today().isoformat()
    entry = f"\n[{today}]\n{content}\n{'─'*40}\n"
    with open(DIARY_FILE, "a", encoding="utf-8") as f:
        f.write(entry)
    print(f"일기가 저장됐습니다. ({today})")

def read_diary() -> None:
    if not DIARY_FILE.exists():
        print("일기가 없습니다.")
        return
    content = DIARY_FILE.read_text(encoding="utf-8")
    print(content)

def search_diary(keyword: str) -> None:
    if not DIARY_FILE.exists():
        return
    found = []
    for line in DIARY_FILE.read_text(encoding="utf-8").splitlines():
        if keyword in line:
            found.append(line)
    if found:
        print(f"'{keyword}' 검색 결과:")
        for line in found:
            print(f"  {line}")
    else:
        print(f"'{keyword}' 를 찾을 수 없습니다.")

write_diary("오늘은 Python 파일 입출력을 배웠다. 매우 유익했다!")
write_diary("FastAPI가 점점 기대된다.")
read_diary()
search_diary("Python")
```

---

## 🧪 LAB 2 – CSV 직접 파싱 (13:00 – 15:00)

```python
# day14_csv.py
from pathlib import Path

CSV_FILE = Path("students.csv")

# CSV 파일 생성
header = "이름,나이,점수,도시\n"
rows   = [
    "홍길동,25,85,서울\n",
    "김철수,22,92,부산\n",
    "이영희,27,78,대구\n",
    "박민준,24,95,인천\n",
]
CSV_FILE.write_text(header + "".join(rows), encoding="utf-8-sig")

# 파싱
def read_csv(path: Path) -> list[dict]:
    records = []
    with open(path, "r", encoding="utf-8-sig") as f:
        headers = [h.strip() for h in f.readline().split(",")]
        for line in f:
            values = [v.strip() for v in line.split(",")]
            records.append(dict(zip(headers, values)))
    return records

students = read_csv(CSV_FILE)
for s in students:
    print(s)

# 점수 기준 정렬 후 재저장
students.sort(key=lambda s: int(s["점수"]), reverse=True)
print("\n점수 순:")
for i, s in enumerate(students, 1):
    print(f"  {i}. {s['이름']}: {s['점수']}점")
```

---

## 🧪 LAB 3 – 로그 파일 분석기 (15:00 – 17:00)

```python
# day14_log_analyzer.py
from pathlib import Path
import random
from datetime import datetime, timedelta

LOG_FILE = Path("app.log")

# 샘플 로그 생성
levels = ["INFO","WARNING","ERROR","DEBUG"]
messages = {
    "INFO":    ["서버 시작","요청 처리 완료","사용자 로그인"],
    "WARNING": ["느린 응답","메모리 사용량 높음"],
    "ERROR":   ["DB 연결 실패","파일 없음","인증 오류"],
    "DEBUG":   ["캐시 히트","쿼리 실행"],
}
base = datetime(2026, 4, 1)
with open(LOG_FILE, "w", encoding="utf-8") as f:
    for i in range(50):
        ts  = (base + timedelta(minutes=i*30)).strftime("%Y-%m-%d %H:%M:%S")
        lvl = random.choice(levels)
        msg = random.choice(messages[lvl])
        f.write(f"[{ts}] {lvl:7s} | {msg}\n")

# 분석
counts = {"INFO":0,"WARNING":0,"ERROR":0,"DEBUG":0}
errors = []
with open(LOG_FILE, "r", encoding="utf-8") as f:
    for line in f:
        for lvl in counts:
            if lvl in line:
                counts[lvl] += 1
                if lvl == "ERROR":
                    errors.append(line.strip())

print("=== 로그 통계 ===")
for lvl, cnt in counts.items():
    print(f"  {lvl:7s}: {cnt}건")
print(f"\n=== 오류 목록 ({len(errors)}건) ===")
for e in errors:
    print(f"  {e}")
```

---

## 📝 과제 (17:00 – 18:00)

`day14_homework.py` – 성적 파일 처리기

1. 10명 학생의 이름과 3과목 점수를 `scores.txt` 에 쓰세요.
2. 파일을 읽어 각 학생의 평균을 계산하세요.
3. 평균 80점 이상 학생을 `passed.txt` 에 저장하세요.
4. 두 파일의 줄 수·크기(bytes)를 `pathlib`으로 출력하세요.

---

## ✅ 체크리스트

- [ ] `open()` 모드 6가지 이해
- [ ] `with` 문으로 파일 안전 처리
- [ ] 일기 앱 (쓰기·읽기·검색) 완성
- [ ] CSV 직접 파싱 완성
- [ ] 로그 파일 생성·분석 완성
- [ ] 성적 파일 처리기 과제 완성

🔎 유튜브 관련 영상 검색: https://www.youtube.com/results?search_query=python+trading+day14+fileio
