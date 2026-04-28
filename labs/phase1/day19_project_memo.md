# Day 19 – 미니 프로젝트: JSON 기반 메모장 앱

> **소요시간**: 8시간 | **Phase**: 1 – Python 완전 기초

---

## 🎯 학습 목표

- Phase 1에서 배운 모든 개념을 하나의 프로젝트에 통합
- 모듈 분리, 예외처리, JSON 파일 I/O, CLI 인터페이스 결합
- 기능: 메모 추가·조회·검색·삭제·태그 필터링

---

## 📋 프로젝트 사양

```
memo_app/
├── __init__.py
├── models.py          # Memo 데이터 클래스
├── storage.py         # JSON 파일 저장소
├── service.py         # 비즈니스 로직
├── cli.py             # CLI 인터페이스
└── main.py            # 진입점
```

**지원 명령어**:
```
add    <제목> <내용> [태그들...]   메모 추가
list                               전체 메모 목록
show   <id>                        특정 메모 상세
search <키워드>                    내용 검색
tag    <태그명>                    태그로 필터링
delete <id>                        메모 삭제
```

---

## 📖 이론 복습 (08:00 – 09:00)

Phase 1 핵심 개념 빠른 리뷰:

| 개념 | 이 프로젝트에서 사용 위치 |
|------|--------------------------|
| 딕셔너리 | Memo 객체 표현 |
| JSON I/O | storage.py – 파일 저장 |
| 예외처리 | service.py – NotFound 등 |
| 모듈/패키지 | memo_app/ 패키지 구조 |
| 리스트 컴프리헨션 | 검색·필터 로직 |
| `sys.argv` | main.py CLI 파싱 |
| `datetime` | 메모 생성/수정 시각 |
| 함수 분리 | 각 모듈별 단일 책임 |

---

## 🧪 LAB 1 – models.py & storage.py (09:00 – 11:00)

```python
# memo_app/models.py
from dataclasses import dataclass, field, asdict
from datetime import datetime

@dataclass
class Memo:
    id:         int
    title:      str
    content:    str
    tags:       list[str]    = field(default_factory=list)
    created_at: str          = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    updated_at: str          = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Memo":
        return cls(**data)
```

```python
# memo_app/storage.py
import json
from pathlib import Path
from .models import Memo

class MemoStorage:
    def __init__(self, path: str = "memos.json"):
        self.path = Path(path)
        if not self.path.exists():
            self._save([])

    def _load(self) -> list[Memo]:
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return [Memo.from_dict(d) for d in data]

    def _save(self, memos: list[Memo]) -> None:
        data = [m.to_dict() for m in memos] if memos else []
        self.path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def get_all(self) -> list[Memo]:
        return self._load()

    def get_by_id(self, memo_id: int) -> Memo | None:
        return next((m for m in self._load() if m.id == memo_id), None)

    def save_memo(self, memo: Memo) -> None:
        memos = self._load()
        for i, m in enumerate(memos):
            if m.id == memo.id:
                memos[i] = memo
                self._save(memos)
                return
        memos.append(memo)
        self._save(memos)

    def delete(self, memo_id: int) -> bool:
        memos = self._load()
        new_memos = [m for m in memos if m.id != memo_id]
        if len(new_memos) == len(memos):
            return False
        self._save(new_memos)
        return True

    def next_id(self) -> int:
        memos = self._load()
        return max((m.id for m in memos), default=0) + 1
```

---

## 🧪 LAB 2 – service.py (11:00 – 13:00)

```python
# memo_app/service.py
from datetime import datetime
from .models import Memo
from .storage import MemoStorage

class MemoNotFoundError(Exception):
    def __init__(self, memo_id: int):
        super().__init__(f"메모 ID {memo_id} 를 찾을 수 없습니다")

class MemoService:
    def __init__(self, storage: MemoStorage | None = None):
        self.storage = storage or MemoStorage()

    def add(self, title: str, content: str, tags: list[str] = None) -> Memo:
        if not title.strip():
            raise ValueError("제목은 비워둘 수 없습니다")
        memo = Memo(
            id      = self.storage.next_id(),
            title   = title.strip(),
            content = content.strip(),
            tags    = [t.lower() for t in (tags or [])],
        )
        self.storage.save_memo(memo)
        return memo

    def get_all(self) -> list[Memo]:
        return self.storage.get_all()

    def get(self, memo_id: int) -> Memo:
        memo = self.storage.get_by_id(memo_id)
        if not memo:
            raise MemoNotFoundError(memo_id)
        return memo

    def search(self, keyword: str) -> list[Memo]:
        kw = keyword.lower()
        return [m for m in self.storage.get_all()
                if kw in m.title.lower() or kw in m.content.lower()]

    def filter_by_tag(self, tag: str) -> list[Memo]:
        tag = tag.lower()
        return [m for m in self.storage.get_all() if tag in m.tags]

    def delete(self, memo_id: int) -> None:
        if not self.storage.delete(memo_id):
            raise MemoNotFoundError(memo_id)
```

---

## 🧪 LAB 3 – cli.py & main.py (14:00 – 17:00)

```python
# memo_app/cli.py
from .service import MemoService, MemoNotFoundError
from .models  import Memo

def fmt_memo_short(m: Memo) -> str:
    tags = " ".join(f"#{t}" for t in m.tags) or "(태그없음)"
    return f"[{m.id:3d}] {m.title:<25} {tags:<20} {m.created_at[:10]}"

def fmt_memo_detail(m: Memo) -> str:
    lines = [
        "=" * 50,
        f"ID      : {m.id}",
        f"제목    : {m.title}",
        f"내용    : {m.content}",
        f"태그    : {', '.join(m.tags) or '없음'}",
        f"생성    : {m.created_at}",
        "=" * 50,
    ]
    return "\n".join(lines)

class CLI:
    def __init__(self):
        self.svc = MemoService()

    def run(self, args: list[str]) -> None:
        if not args:
            print("명령어: add | list | show | search | tag | delete")
            return
        cmd, *rest = args
        try:
            getattr(self, f"cmd_{cmd}", self.cmd_unknown)(rest)
        except MemoNotFoundError as e:
            print(f"❌ {e}")
        except ValueError as e:
            print(f"⚠️ {e}")

    def cmd_add(self, args):
        if len(args) < 2:
            print("사용법: add <제목> <내용> [태그...]"); return
        title, content, *tags = args
        memo = self.svc.add(title, content, tags)
        print(f"✅ 메모 추가됨 (ID: {memo.id}): {memo.title}")

    def cmd_list(self, _):
        memos = self.svc.get_all()
        if not memos:
            print("메모가 없습니다.")
        else:
            print(f"{'ID':>4} {'제목':<25} {'태그':<20} {'날짜'}")
            print("-" * 60)
            for m in memos:
                print(fmt_memo_short(m))

    def cmd_show(self, args):
        if not args: print("사용법: show <id>"); return
        print(fmt_memo_detail(self.svc.get(int(args[0]))))

    def cmd_search(self, args):
        if not args: print("사용법: search <키워드>"); return
        results = self.svc.search(args[0])
        print(f"'{args[0]}' 검색 결과: {len(results)}건")
        for m in results: print(fmt_memo_short(m))

    def cmd_tag(self, args):
        if not args: print("사용법: tag <태그명>"); return
        results = self.svc.filter_by_tag(args[0])
        print(f"#{args[0]} 태그 메모: {len(results)}건")
        for m in results: print(fmt_memo_short(m))

    def cmd_delete(self, args):
        if not args: print("사용법: delete <id>"); return
        self.svc.delete(int(args[0]))
        print(f"✅ 메모 ID {args[0]} 삭제됨")

    def cmd_unknown(self, _):
        print("알 수 없는 명령어")
```

```python
# memo_app/main.py
import sys
from .cli import CLI

if __name__ == "__main__":
    CLI().run(sys.argv[1:])
```

실행 예시:
```bash
python -m memo_app add "Python 기초" "변수, 자료형, 함수 학습 완료" python 기초
python -m memo_app add "FastAPI 시작" "uvicorn 설치 및 첫 API 작성" fastapi python
python -m memo_app list
python -m memo_app show 1
python -m memo_app search "python"
python -m memo_app tag python
python -m memo_app delete 2
```

---

## 📝 과제 & 도전 (17:00 – 18:00)

1. **수정 기능 추가**: `update <id> <제목> <내용>` 명령어 구현
2. **즐겨찾기 기능**: `Memo`에 `starred: bool` 필드 추가, `star <id>` 명령어
3. **내보내기**: `export` 명령어로 전체 메모를 마크다운 파일로 저장

---

## ✅ 체크리스트

- [ ] `memo_app/` 패키지 구조 완성
- [ ] `Memo` 데이터클래스 구현
- [ ] `MemoStorage` JSON CRUD 완성
- [ ] `MemoService` 비즈니스 로직 완성
- [ ] `CLI` add/list/show/search/tag/delete 완성
- [ ] 최소 5개 이상 메모 추가 후 전 기능 테스트
- [ ] 도전 기능 1가지 이상 완성
