# Phase 6 – FastAPI 고급 & 실전 프로젝트 (Day 101 ~ 120)

> **기간**: Day 101 – 120 | **총 160시간**

---

## 📋 Phase 6 학습 로드맵

| Day | 주제 | 핵심 키워드 |
|-----|------|------------|
| 101 | WebSocket 기초 | `WebSocket`, 실시간 채팅 |
| 102 | WebSocket 심화 | 룸, 브로드캐스트, 연결 관리 |
| 103 | Celery + Redis | 비동기 작업 큐 |
| 104 | SSE | `StreamingResponse`, 서버 푸시 |
| 105 | GraphQL | `strawberry-graphql` |
| 106 | Docker 기초 | Dockerfile, 이미지, 컨테이너 |
| 107 | Docker Compose | 멀티 컨테이너 (FastAPI + DB + Redis) |
| 108 | CI/CD | GitHub Actions 파이프라인 |
| 109 | 클라우드 배포 | Railway / Render / Fly.io |
| 110 | 성능 최적화 | 프로파일링, N+1, 인덱스 |
| 111 | 보안 강화 | Rate Limiting, SQL Injection |
| 112 | 모니터링 | Prometheus, Sentry |
| 113 | 최종 프로젝트 설계 | 요구사항, ERD, API 설계 |
| 114 | 최종 프로젝트 개발 1 | 모델 & 인증 |
| 115 | 최종 프로젝트 개발 2 | 핵심 API |
| 116 | 최종 프로젝트 개발 3 | 파일 업로드·이메일 |
| 117 | 최종 프로젝트 개발 4 | 테스트 작성 |
| 118 | 최종 프로젝트 개발 5 | Docker & 배포 |
| 119 | 발표 준비 | 코드 리뷰·문서화 |
| 120 | 최종 발표 & 수료식 | 데모, 질의응답 |

---

# Day 101 – WebSocket 기초

## 🎯 학습 목표

- WebSocket 프로토콜 이해 (HTTP 업그레이드)
- FastAPI `WebSocket` 엔드포인트 구현
- 브라우저 JavaScript WebSocket API 연동

## 📖 이론 (08:00 – 10:00)

```
HTTP:      요청 → 응답 (1:1, 단방향)
WebSocket: 연결 → 양방향 실시간 통신
           ┌──────────────┐
 Client ←──┤  WebSocket   ├──→ Server
           │  (유지 연결)  │
           └──────────────┘
```

## 🧪 LAB 실습 (10:00 – 17:00)

```python
# day101_websocket.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()

# 연결 관리자
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self.active_connections.append(ws)
        print(f"연결됨: {len(self.active_connections)}명 온라인")

    def disconnect(self, ws: WebSocket) -> None:
        self.active_connections.remove(ws)
        print(f"연결 종료: {len(self.active_connections)}명 온라인")

    async def send_personal(self, message: str, ws: WebSocket) -> None:
        await ws.send_text(message)

    async def broadcast(self, message: str) -> None:
        for conn in self.active_connections:
            await conn.send_text(message)

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def chat_page():
    return """
    <!DOCTYPE html>
    <html>
    <head><title>실시간 채팅</title></head>
    <body>
        <h2>실시간 채팅방 💬</h2>
        <input type="text" id="nickname" placeholder="닉네임" value="익명">
        <br><br>
        <div id="chat" style="border:1px solid #ccc; height:300px; overflow:auto; padding:10px;"></div>
        <br>
        <input type="text" id="msg" placeholder="메시지 입력..." style="width:300px">
        <button onclick="sendMsg()">전송</button>

        <script>
            const ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = e => {
                const div = document.getElementById('chat');
                div.innerHTML += '<p>' + e.data + '</p>';
                div.scrollTop = div.scrollHeight;
            };
            function sendMsg() {
                const nick = document.getElementById('nickname').value;
                const msg  = document.getElementById('msg').value;
                if (msg.trim()) {
                    ws.send(JSON.stringify({nickname: nick, message: msg}));
                    document.getElementById('msg').value = '';
                }
            }
            document.getElementById('msg').addEventListener('keypress', e => {
                if (e.key === 'Enter') sendMsg();
            });
        </script>
    </body>
    </html>
    """

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            data = await ws.receive_json()
            nick = data.get("nickname", "익명")
            msg  = data.get("message", "")
            await manager.broadcast(f"[{nick}] {msg}")
    except WebSocketDisconnect:
        manager.disconnect(ws)
        await manager.broadcast(f"[시스템] 누군가 퇴장했습니다")
```

---

# Day 102 – WebSocket 심화: 채팅 룸

```python
# day102_chat_rooms.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from collections import defaultdict
import json, datetime

app = FastAPI()

class RoomManager:
    def __init__(self):
        self.rooms: dict[str, list[WebSocket]] = defaultdict(list)
        self.user_names: dict[WebSocket, str] = {}

    async def join(self, room_id: str, ws: WebSocket, nickname: str) -> None:
        await ws.accept()
        self.rooms[room_id].append(ws)
        self.user_names[ws] = nickname
        await self.broadcast(room_id, "시스템", f"{nickname}님이 입장했습니다 👋", exclude=None)

    async def leave(self, room_id: str, ws: WebSocket) -> None:
        nick = self.user_names.pop(ws, "알 수 없음")
        if ws in self.rooms[room_id]:
            self.rooms[room_id].remove(ws)
        await self.broadcast(room_id, "시스템", f"{nick}님이 퇴장했습니다", exclude=None)

    async def broadcast(self, room_id: str, sender: str, message: str, exclude: WebSocket | None) -> None:
        payload = json.dumps({
            "sender":    sender,
            "message":   message,
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
            "room":      room_id,
            "users":     len(self.rooms[room_id]),
        }, ensure_ascii=False)
        for conn in self.rooms[room_id]:
            if conn != exclude:
                await conn.send_text(payload)

    def get_online_count(self, room_id: str) -> int:
        return len(self.rooms[room_id])

mgr = RoomManager()

@app.websocket("/ws/{room_id}/{nickname}")
async def room_chat(ws: WebSocket, room_id: str, nickname: str):
    await mgr.join(room_id, ws, nickname)
    try:
        while True:
            msg = await ws.receive_text()
            await mgr.broadcast(room_id, nickname, msg, exclude=ws)
    except WebSocketDisconnect:
        await mgr.leave(room_id, ws)

@app.get("/rooms/{room_id}/count")
async def room_count(room_id: str):
    return {"room": room_id, "online": mgr.get_online_count(room_id)}
```

---

# Day 106-107 – Docker & Docker Compose

## Day 106 – Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 의존성 레이어 (캐싱 최적화)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# 포트 노출
EXPOSE 8000

# 실행 명령
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# 이미지 빌드
docker build -t fastapi-app:1.0 .

# 컨테이너 실행
docker run -d -p 8000:8000 --name my-api fastapi-app:1.0

# 로그 확인
docker logs my-api -f

# 컨테이너 중지/삭제
docker stop my-api && docker rm my-api
```

## Day 107 – Docker Compose

```yaml
# docker-compose.yml
version: "3.9"

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
      - SECRET_KEY=your-secret-key
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - .:/app    # 개발용 핫 리로드
    command: uvicorn app:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER:     user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB:       mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL","pg_isready -U user"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD","redis-cli","ping"]
      interval: 5s
      timeout: 3s
      retries: 5

volumes:
  postgres_data:
```

```bash
# 실행
docker-compose up --build -d

# 로그
docker-compose logs -f api

# 중지
docker-compose down
```

---

# Day 108 – GitHub Actions CI/CD

```yaml
# .github/workflows/ci.yml
name: FastAPI CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Python 설정
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip

      - name: 의존성 설치
        run: pip install -r requirements.txt

      - name: 린트
        run: |
          pip install ruff
          ruff check .

      - name: 테스트
        run: pytest tests/ -v --cov=. --cov-report=xml

      - name: 커버리지 업로드
        uses: codecov/codecov-action@v4

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4

      - name: Railway 배포
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: |
          npm install -g @railway/cli
          railway deploy
```

---

# Day 113 – 최종 프로젝트 설계

## 📋 프로젝트 주제 예시

수강생이 아래 중 하나를 선택하거나 자유 주제 제안:

| 번호 | 주제 | 핵심 기술 |
|------|------|-----------|
| 1 | 쇼핑몰 백엔드 | 상품·주문·결제·리뷰 |
| 2 | SNS 플랫폼 | 피드·팔로우·좋아요·DM |
| 3 | 온라인 강의 플랫폼 | 강의·수강·퀴즈·수료증 |
| 4 | 실시간 협업 메모앱 | WebSocket·버전관리 |
| 5 | 채용 플랫폼 | 공고·지원·면접 일정 |

## 설계 산출물 (Day 113 까지 완성)

### 1. 요구사항 명세서

```markdown
## 프로젝트: [제목]

### 기능 요구사항
- 회원: 회원가입, 로그인(JWT), 프로필 관리
- [도메인별 기능 목록]

### 비기능 요구사항
- 응답시간: 일반 API 200ms 이하
- 테스트 커버리지: 80% 이상
- Docker 배포 필수
```

### 2. ERD (Entity-Relationship Diagram)

```
User ──<─── Post ──<─── Comment
  │                        │
  └──<─── Like ───>────────┘
  │
  └──<─── Follow ──>── User
```

### 3. API 명세

| Method | Endpoint | Auth | 설명 |
|--------|----------|------|------|
| ... | ... | ... | ... |

---

# Day 114-118 – 최종 프로젝트 개발

## Day 114 – 모델 & 인증 구현

```python
# 프로젝트 공통 구조 (예: 쇼핑몰)
final_project/
├── main.py
├── database.py
├── models/
│   ├── user.py
│   ├── product.py
│   ├── order.py
│   └── review.py
├── schemas/
│   ├── user.py
│   ├── product.py
│   ├── order.py
│   └── review.py
├── routers/
│   ├── auth.py
│   ├── users.py
│   ├── products.py
│   ├── orders.py
│   └── reviews.py
├── auth/
│   ├── jwt.py
│   └── deps.py
├── services/
│   ├── email.py      # 주문 확인 이메일
│   └── file.py       # 상품 이미지 업로드
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_products.py
│   └── test_orders.py
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## Day 115 – 핵심 API 구현 체크리스트

- [ ] 회원가입 / 로그인 (JWT)
- [ ] 본인 정보 조회·수정
- [ ] 상품 CRUD (admin 권한)
- [ ] 상품 목록 (페이지네이션, 필터, 정렬)
- [ ] 주문 생성·조회·취소
- [ ] 리뷰 작성·수정·삭제

## Day 116 – 부가 기능

- [ ] 상품 이미지 업로드 (`UploadFile`)
- [ ] 주문 완료 이메일 (`fastapi-mail`)
- [ ] 재고 캐싱 (`lru_cache`)

## Day 117 – 테스트

```
목표: 핵심 엔드포인트 80% 이상 커버리지
```

- [ ] auth 테스트 (로그인 성공/실패, 토큰 만료)
- [ ] products 테스트 (CRUD, 권한 검사)
- [ ] orders 테스트 (생성, 재고 차감, 취소)
- [ ] fixtures: 테스트 DB, 인증 유저, 샘플 데이터

## Day 118 – Docker & 배포

```bash
# 최종 빌드 및 테스트
docker-compose up --build -d
docker-compose exec api pytest tests/ -v

# 클라우드 배포 (Railway 예시)
railway login
railway init
railway up
```

---

# Day 119 – 발표 준비

## 발표 자료 구성 (15분)

```
1. 프로젝트 소개 (2분)
   - 주제 선택 이유
   - 해결하는 문제

2. 기술 스택 & 아키텍처 (3분)
   - ERD 설명
   - 주요 기술 선택 이유

3. 라이브 데모 (7분)
   - Swagger UI에서 API 시연
   - WebSocket / 실시간 기능 (있다면)

4. 코드 하이라이트 (2분)
   - 가장 자신 있는 코드 1-2개
   - 어려웠던 점 & 해결 방법

5. Q&A (1분)
```

## 코드 리뷰 체크리스트

- [ ] 함수/클래스 독스트링 작성
- [ ] 환경변수로 민감 정보 분리 (.env)
- [ ] 에러 핸들링 일관성
- [ ] 로깅 적용
- [ ] README.md 완성 (설치·실행·API 문서)
- [ ] 테스트 커버리지 리포트 첨부

---

# Day 120 – 최종 발표 & 수료식 🎓

## 🏆 수료 기준

| 항목 | 기준 | 배점 |
|------|------|------|
| 일일 LAB 과제 제출률 | 80% 이상 | 40점 |
| Phase 미니 프로젝트 | 6개 모두 완성 | 30점 |
| 최종 프로젝트 | 아래 기준 충족 | 30점 |

### 최종 프로젝트 평가 기준 (30점)

| 항목 | 배점 |
|------|------|
| 기능 완성도 | 10 |
| 코드 품질 (가독성·구조) | 5 |
| 테스트 커버리지 (80%+) | 5 |
| Docker 배포 성공 | 5 |
| 발표 & Q&A | 5 |

---

## 🎯 120일 후 달성 역량

```
✅ Python 완전 기초 → 고급 (비동기, 데코레이터, 타입 힌트)
✅ FastAPI 기초 → 중급 (DB, 인증, 테스트)
✅ 실전 프로젝트 설계 → 개발 → 배포 전 과정 경험
✅ 코드 리뷰 문화 및 Git 협업 경험
✅ Docker 컨테이너화 및 클라우드 배포
```

## 다음 학습 로드맵

```
이 커리큘럼 이후 권장 학습:

1. PostgreSQL + 비동기 SQLAlchemy (AsyncSession)
2. Redis 고급 (Pub/Sub, Stream)
3. Kubernetes 기초
4. 마이크로서비스 아키텍처
5. gRPC + Protocol Buffers
6. 코드 리뷰 & 오픈소스 기여
```

---

*축하합니다! 120일간의 여정을 완주하셨습니다! 🎉*
