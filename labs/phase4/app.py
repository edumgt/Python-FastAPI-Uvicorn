# FastAPI 웹 프레임워크에서 애플리케이션 객체를 가져온다.
from fastapi import FastAPI

# 패키지 실행(uvicorn labs.phase4.app:app) 시 사용할 상대 경로 import를 시도한다.
try:
    # phase4 폴더 안의 mydata 모듈에서 사용자 데이터 함수만 가져온다.
    from .mydata import get_data
    # phase4 폴더 안의 hashtest 모듈에서 과일 정보 함수만 가져온다.
    from .hashtest import get_fruits_info
# 파일 단독 실행처럼 상대 import가 실패하는 상황을 처리한다.
except ImportError:
    # 같은 폴더 기준 절대 경로 스타일로 mydata 함수를 다시 가져온다.
    from mydata import get_data
    # 같은 폴더 기준 절대 경로 스타일로 hashtest 함수를 다시 가져온다.
    from hashtest import get_fruits_info

# FastAPI 서버 인스턴스를 생성하여 라우트를 등록할 준비를 한다.
app = FastAPI()

# 루트 경로("/")에 GET 요청이 오면 아래 함수를 실행하도록 연결한다.
@app.get("/")
# 비동기 루트 핸들러를 선언한다.
async def root():
    # 기본 연결 확인용 메시지를 JSON 형태로 반환한다.
    return {"message": "Hello, FastAPI!"}

# "/user" 경로에 GET 요청이 오면 사용자 정보 핸들러를 실행하도록 연결한다.
@app.get("/user")
# 사용자 정보 응답을 위한 비동기 함수를 선언한다.
async def user_info():
    # mydata 모듈에서 만든 딕셔너리 데이터를 그대로 반환한다.
    return get_data()

# "/fruits" 경로에 GET 요청이 오면 과일 정보 핸들러를 실행하도록 연결한다.
@app.get("/fruits")
# 과일 정보 응답을 위한 비동기 함수를 선언한다.
async def fruits_info():
    # hashtest 모듈에서 만든 집합(set) 기반 정보를 반환한다.
    return get_fruits_info()
