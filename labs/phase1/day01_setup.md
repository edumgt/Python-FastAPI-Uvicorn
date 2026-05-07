# Day 01 – 개발환경 구축

> **소요시간**: 8시간 | **Phase**: 1 – Python 완전 기초

---

## 🎯 학습 목표

- Python 3.10+ 설치 및 버전 확인
- `venv` 가상환경 생성·활성화·비활성화
- VSCode + Python 확장 설치 및 기본 설정
- `pip`로 패키지 설치 및 `requirements.txt` 생성
- 첫 번째 파이썬 스크립트 실행

---

## 📖 이론 (08:00 – 10:00)

### 1. Python 이란?
- 인터프리터 언어 · 동적 타입 · 범용 언어
- 버전: CPython 3.10 / 3.11 / 3.13 (이 과정: **3.10 이상 권장**)

### 2. 가상환경(venv)이 필요한 이유
- 프로젝트마다 독립적인 패키지 버전 관리
- 시스템 Python 오염 방지

### 3. pip & requirements.txt
```bash
pip install <패키지>           # 설치
pip list                       # 설치된 패키지 목록
pip freeze > requirements.txt  # 현재 환경 저장
pip install -r requirements.txt # 환경 복원
```

---

## 🧪 LAB 1 – 환경 설치 (10:00 – 12:00)

### Step 1: Python 버전 확인
```bash
python --version   # Python 3.x.x
python3 --version  # (macOS/Linux)
```

### Step 2: 프로젝트 폴더 생성
```bash
mkdir my_python_project
cd my_python_project
```

### Step 3: 가상환경 생성 및 활성화
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

활성화 확인 – 프롬프트 앞에 `(venv)` 가 붙어야 합니다.

### Step 4: VSCode 열기
```bash
code .
```
- **Python 확장** (ms-python.python) 설치 확인
- 우측 하단 Python 인터프리터를 `./venv` 로 변경

---

## 🧪 LAB 2 – 첫 번째 스크립트 (13:00 – 15:00)

`hello.py` 파일을 만들고 아래 코드를 작성하세요.

```python
# hello.py
print("안녕하세요, Python!")
print(f"Python 버전: {__import__('sys').version}")
```

실행:
```bash
python hello.py
```

**예상 출력**:
```
안녕하세요, Python!
Python 버전: 3.10.x (...)
```

---

## 🧪 LAB 3 – pip & requirements.txt (15:00 – 17:00)

```bash
# requests 패키지 설치 (예시)
pip install requests

# 설치 확인
pip list

# requirements.txt 생성
pip freeze > requirements.txt
cat requirements.txt

# 가상환경 비활성화
deactivate
```

새 터미널에서 환경 복원 테스트:
```bash
python -m venv venv_test
source venv_test/bin/activate  # Windows: venv_test\Scripts\activate
pip install -r requirements.txt
pip list
deactivate
```

---

## 📝 과제 (17:00 – 18:00)

1. 새 폴더 `day01_homework`를 만들고 가상환경을 생성하세요.
2. `fpdf2` 패키지를 설치하고 `requirements.txt`를 생성하세요.
3. `info.py`를 작성하여 아래 정보를 출력하는 스크립트를 완성하세요.

```python
# info.py – 완성하세요
import sys
import platform

print("=== 내 개발 환경 정보 ===")
print(f"Python 버전  : {sys.version}")
print(f"운영체제     : {platform.system()} {platform.release()}")
print(f"Python 경로  : {sys.executable}")
```

4. 실행 결과를 캡처하여 제출하세요.

---

## ✅ 체크리스트

- [ ] Python 3.10+ 설치 완료
- [ ] `venv` 생성·활성화·비활성화 성공
- [ ] VSCode Python 인터프리터 설정 완료
- [ ] `hello.py` 실행 성공
- [ ] `requirements.txt` 생성 및 복원 성공
- [ ] 과제 `info.py` 제출

---

## 📚 참고자료

- [Python 공식 다운로드](https://www.python.org/downloads/)
- [venv 공식 문서](https://docs.python.org/3/library/venv.html)
- [VSCode Python 확장](https://marketplace.visualstudio.com/items?itemName=ms-python.python)

🔎 유튜브 관련 영상 검색: https://www.youtube.com/results?search_query=python+trading+day01+setup
