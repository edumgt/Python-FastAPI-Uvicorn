# 파이썬 객체를 JSON 문자열로 바꿀 때 사용할 json 모듈을 불러온다.
import json

# 해시맵(dict) 생성과 JSON 직렬화 동작을 보여주는 메인 함수를 정의한다.
def main():
    # 키-값 쌍으로 구성된 딕셔너리 데이터를 생성한다.
    data = {
        # 이름 정보를 name 키에 저장한다.
        "name": "홍길동",
        # 나이 정보를 age 키에 저장한다.
        "age": 25,
        # 이메일 정보를 email 키에 저장한다.
        "email": "hong@example.com",
    }

    # 딕셔너리를 한글이 유지되는 JSON 문자열로 변환한다.
    json_string = json.dumps(data, ensure_ascii=False)
    # 변환된 JSON 문자열을 콘솔에 출력한다.
    print("JSON 출력:", json_string)

# 현재 파일을 직접 실행한 경우에만 아래 블록을 실행한다.
if __name__ == "__main__":
    # 메인 함수를 호출해 예제를 실행한다.
    main()
