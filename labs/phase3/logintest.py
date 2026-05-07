# JSON 파일 입출력을 위해 json 모듈을 불러온다.
import json
# 파일 경로를 안전하게 다루기 위해 pathlib의 Path 클래스를 불러온다.
from pathlib import Path

# 현재 파일 위치를 기준으로 저장소 루트 경로를 계산한다.
BASE_DIR = Path(__file__).resolve().parents[2]
# 사용자 계정 원본 데이터 파일 경로를 절대 경로로 구성한다.
USERS_FILE = BASE_DIR / "users.json"
# 로그인 상태 저장 파일 경로를 절대 경로로 구성한다.
LOGIN_FILE = BASE_DIR / "loginusers.json"

# users.json에서 전체 사용자 정보를 읽어오는 함수를 정의한다.
def load_users():
    # UTF-8 인코딩으로 사용자 파일을 읽기 모드로 연다.
    with USERS_FILE.open("r", encoding="utf-8") as file_handle:
        # JSON 텍스트를 파이썬 딕셔너리로 변환해 반환한다.
        return json.load(file_handle)

# loginusers.json에서 현재 로그인 사용자 목록을 읽어오는 함수를 정의한다.
def load_login_users():
    # 로그인 상태 파일이 아직 없으면 빈 리스트를 반환한다.
    if not LOGIN_FILE.exists():
        # 로그인 사용자가 없다는 의미로 빈 리스트를 즉시 반환한다.
        return []
    # 로그인 상태 파일이 있으면 UTF-8 인코딩으로 읽기 모드로 연다.
    with LOGIN_FILE.open("r", encoding="utf-8") as file_handle:
        # JSON 배열을 파이썬 리스트로 변환해 반환한다.
        return json.load(file_handle)

# 로그인 사용자 목록을 loginusers.json에 저장하는 함수를 정의한다.
def save_login_users(login_users):
    # UTF-8 인코딩으로 파일을 쓰기 모드로 열어 기존 내용을 갱신한다.
    with LOGIN_FILE.open("w", encoding="utf-8") as file_handle:
        # 리스트를 보기 쉬운 들여쓰기 JSON으로 저장한다.
        json.dump(login_users, file_handle, ensure_ascii=False, indent=4)

# 콘솔 로그인 시뮬레이션을 실행하는 메인 함수를 정의한다.
def main():
    # 등록된 전체 사용자 정보를 메모리로 로드한다.
    users = load_users()
    # 현재 로그인 상태 사용자 목록을 메모리로 로드한다.
    login_users = load_login_users()

    # 올바른 로그인 입력이 들어올 때까지 무한 반복한다.
    while True:
        # 사용자에게 아이디 입력을 요청한다.
        user_id = input("아이디 입력해 주세요: ")
        # 사용자에게 비밀번호 입력을 요청한다.
        password = input("비번 입력해 주세요: ")
        # 입력 구간과 결과 메시지를 구분하기 위해 빈 줄을 출력한다.
        print("")

        # 입력된 아이디가 사용자 목록에 존재하는지 확인한다.
        if user_id in users:
            # 존재하는 아이디의 비밀번호가 입력값과 일치하는지 확인한다.
            if users[user_id] == password:
                # 이미 로그인된 사용자라면 중복 로그인을 막는다.
                if user_id in login_users:
                    # 중복 로그인 금지 안내 메시지를 출력한다.
                    print("이미 로그인 상태입니다. 중복 로그인 불가!")
                else:
                    # 정상 로그인 성공 메시지를 출력한다.
                    print("Login Success ✅")
                    # 로그인 목록에 현재 아이디를 추가한다.
                    login_users.append(user_id)
                    # 갱신된 로그인 목록을 파일에 저장한다.
                    save_login_users(login_users)
                    # 성공 처리 후 반복문을 종료해 프로그램을 끝낸다.
                    break
            else:
                # 비밀번호가 일치하지 않을 때 실패 메시지를 출력한다.
                print("Login Fail (비밀번호 오류)")
        else:
            # 아이디가 존재하지 않을 때 안내 메시지를 출력한다.
            print("Login ID Not Exist")

# 현재 파일이 직접 실행되는 경우에만 메인 함수를 호출한다.
if __name__ == "__main__":
    # 로그인 시뮬레이션을 시작한다.
    main()
