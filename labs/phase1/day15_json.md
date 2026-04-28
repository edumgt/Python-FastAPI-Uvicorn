# Day 15 – JSON 처리

> **소요시간**: 8시간 | **Phase**: 1 – Python 완전 기초

---

## 🎯 학습 목표

- `json.dumps()` / `json.loads()` – 직렬화·역직렬화
- `json.dump()` / `json.load()` – 파일 I/O
- 중첩 JSON 탐색 및 변환
- `users.json` / `loginusers.json` 기반 실습 (이 repo 연동)

---

## 📖 이론 (08:00 – 10:00)

```python
import json

# 직렬화 (Python dict → JSON 문자열)
data = {"name":"홍길동", "age":25, "scores":[85,92,78], "active":True, "addr":None}
json_str = json.dumps(data, ensure_ascii=False, indent=2)
print(json_str)

# 역직렬화 (JSON 문자열 → Python dict)
parsed = json.loads(json_str)
print(type(parsed), parsed["name"])

# 파일 저장
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# 파일 읽기
with open("data.json", "r", encoding="utf-8") as f:
    loaded = json.load(f)
print(loaded)

# JSON 타입 매핑
# Python dict  ↔ JSON object {}
# Python list  ↔ JSON array  []
# Python str   ↔ JSON string ""
# Python int/float ↔ JSON number
# Python True/False ↔ JSON true/false
# Python None  ↔ JSON null
```

---

## 🧪 LAB 1 – 이 repo의 logintest.py 확장 (10:00 – 12:00)

```python
# day15_json_login.py  (logintest.py 코드 기반 확장)
import json
import os
from pathlib import Path
from datetime import datetime

USERS_FILE      = Path("users.json")
LOGIN_FILE      = Path("loginusers.json")
LOGIN_LOG_FILE  = Path("login_log.json")

# users.json 초기화 (없을 경우)
if not USERS_FILE.exists():
    users = {"admin":"admin123","user1":"pass1","user2":"pass2"}
    USERS_FILE.write_text(json.dumps(users, indent=2), encoding="utf-8")

def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))

def save_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def login(user_id: str, pw: str) -> str:
    users       = load_json(USERS_FILE, {})
    login_users = load_json(LOGIN_FILE, [])
    log         = load_json(LOGIN_LOG_FILE, [])
    ts = datetime.now().isoformat(timespec="seconds")

    if user_id not in users:
        msg = "ID 없음"
    elif users[user_id] != pw:
        msg = "비밀번호 오류"
    elif user_id in login_users:
        msg = "이미 로그인 중"
    else:
        login_users.append(user_id)
        save_json(LOGIN_FILE, login_users)
        msg = "로그인 성공 ✅"

    log.append({"ts":ts,"id":user_id,"result":msg})
    save_json(LOGIN_LOG_FILE, log)
    return msg

# 테스트
for uid, pw in [("admin","admin123"),("user1","wrong"),("user1","pass1"),("user1","pass1")]:
    print(f"  {uid}/{pw} → {login(uid, pw)}")

print("\n로그인 로그:")
for entry in load_json(LOGIN_LOG_FILE, []):
    print(f"  [{entry['ts']}] {entry['id']}: {entry['result']}")
```

---

## 🧪 LAB 2 – 중첩 JSON 처리 (13:00 – 15:00)

```python
# day15_nested_json.py
import json

api_response = '''
{
  "status": "success",
  "data": {
    "users": [
      {"id":1,"name":"홍길동","profile":{"city":"서울","job":"개발자"},"tags":["python","fastapi"]},
      {"id":2,"name":"김철수","profile":{"city":"부산","job":"디자이너"},"tags":["figma","css"]},
      {"id":3,"name":"이영희","profile":{"city":"서울","job":"데이터분석가"},"tags":["python","pandas"]}
    ],
    "total": 3
  }
}
'''

data = json.loads(api_response)
users = data["data"]["users"]

# 1. 서울 거주 유저 이름
seoul_users = [u["name"] for u in users if u["profile"]["city"] == "서울"]
print("서울 거주:", seoul_users)

# 2. python 태그 유저
python_users = [u["name"] for u in users if "python" in u["tags"]]
print("python 태그:", python_users)

# 3. 모든 태그 집합
all_tags = set(tag for u in users for tag in u["tags"])
print("전체 태그:", sorted(all_tags))

# 4. id → 유저 매핑 딕셔너리
id_map = {u["id"]: u["name"] for u in users}
print("ID 맵:", id_map)
```

---

## 🧪 LAB 3 – JSON 기반 간단 DB (15:00 – 17:00)

```python
# day15_json_db.py
import json
from pathlib import Path

DB_FILE = Path("db.json")

class JsonDB:
    """JSON 파일을 간단한 Key-Value DB로 사용"""

    def __init__(self, path: Path):
        self.path = path
        if not path.exists():
            self._save({})

    def _load(self) -> dict:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, data: dict) -> None:
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def set(self, key: str, value) -> None:
        db = self._load(); db[key] = value; self._save(db)

    def get(self, key: str, default=None):
        return self._load().get(key, default)

    def delete(self, key: str) -> bool:
        db = self._load()
        if key not in db: return False
        del db[key]; self._save(db); return True

    def keys(self) -> list:
        return list(self._load().keys())

db = JsonDB(DB_FILE)
db.set("counter", 0)
db.set("fruits", ["apple","banana"])
db.set("config", {"debug":True,"port":8000})

print(db.get("counter"))        # 0
print(db.get("fruits"))         # ['apple', 'banana']
db.set("counter", db.get("counter") + 1)
print(db.get("counter"))        # 1
print(db.keys())
db.delete("config")
print(db.keys())
```

---

## 📝 과제 (17:00 – 18:00)

`day15_homework.py` – API 응답 파서

1. 아래 형태의 공공 API 응답 JSON 문자열을 `json.loads()`로 파싱하세요.
2. 날짜별 최고/최저 온도, 평균 습도를 계산하세요.
3. 결과를 `weather_summary.json`으로 저장하세요.

```json
{"weather":[
  {"date":"2026-04-01","temp_high":18,"temp_low":8,"humidity":65},
  {"date":"2026-04-02","temp_high":22,"temp_low":12,"humidity":55},
  {"date":"2026-04-03","temp_high":15,"temp_low":7,"humidity":80}
]}
```

---

## ✅ 체크리스트

- [ ] `dumps/loads/dump/load` 4가지 구분
- [ ] `ensure_ascii=False`, `indent` 옵션 활용
- [ ] logintest.py 기반 로그인 로그 JSON 완성
- [ ] 중첩 JSON 탐색·변환 완성
- [ ] JsonDB 클래스 구현 완성
- [ ] 날씨 API 파서 과제 완성
