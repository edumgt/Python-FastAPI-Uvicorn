# 파이썬 객체를 JSON 문자열로 직렬화할 때 사용할 json 모듈을 가져온다.
import json

# 사용자 예시 데이터를 딕셔너리 형태로 만들어 반환하는 함수를 정의한다.
def get_data():
    # 학습용 사용자 정보를 담는 딕셔너리 객체를 만든다.
    data = {
        # 사용자 이름 키에 문자열 값을 저장한다.
        "name": "홍길동",
        # 사용자 나이 키에 정수 값을 저장한다.
        "age": 25,
        # 사용자 이메일 키에 문자열 값을 저장한다.
        "email": "hong@example.com",
    }
    # 완성된 딕셔너리를 호출한 쪽으로 돌려준다.
    return data

# 스크립트를 직접 실행했을 때 동작할 테스트용 메인 함수를 정의한다.
def main():
    # 딕셔너리를 한글이 깨지지 않는 JSON 문자열로 변환한다.
    json_string = json.dumps(get_data(), ensure_ascii=False)
    # 변환된 JSON 문자열을 콘솔에 출력한다.
    print("JSON 출력:", json_string)

# 현재 파일이 엔트리 포인트로 직접 실행되는 경우만 아래 블록을 실행한다.
if __name__ == "__main__":
    # 메인 함수를 호출해 데모 출력을 수행한다.
    main()
