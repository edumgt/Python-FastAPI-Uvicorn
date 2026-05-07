# 파일 역할을 식별하기 위한 모듈 설명 주석을 남긴다.
# HashSetExample.py

# 과일 집합 예제를 실행하고 결과를 딕셔너리로 반환하는 함수를 정의한다.
def get_fruits_info():
    # 중복을 자동 제거하는 set 컬렉션을 비어 있는 상태로 만든다.
    fruits = set()

    # 문자열 "Apple"을 집합에 추가한다.
    fruits.add("Apple")
    # 문자열 "Banana"를 집합에 추가한다.
    fruits.add("Banana")
    # 문자열 "Orange"를 집합에 추가한다.
    fruits.add("Orange")
    # 중복된 "Apple"을 다시 넣어도 set 특성상 하나만 유지된다.
    fruits.add("Apple")

    # API 응답에 사용할 결과 딕셔너리를 빈 상태로 생성한다.
    info = {}
    # 현재 과일 개수를 계산해 "초기_과일_개수" 키에 저장한다.
    info["초기_과일_개수"] = len(fruits)
    # set은 JSON 직렬화가 어려우므로 list로 변환해 "초기_과일_목록"에 저장한다.
    info["초기_과일_목록"] = list(fruits)
    # "Banana" 존재 여부를 불리언으로 계산해 "Banana_포함"에 저장한다.
    info["Banana_포함"] = "Banana" in fruits

    # 집합에서 "Orange" 항목을 제거한다.
    fruits.remove("Orange")
    # 제거 후 상태를 list로 바꿔 "Orange_제거_후" 키에 저장한다.
    info["Orange_제거_후"] = list(fruits)

    # 정리된 결과 딕셔너리를 호출자에게 반환한다.
    return info


# 모듈 단독 실행 시 결과를 확인하기 위한 메인 함수를 정의한다.
def main():
    # 과일 정보 함수를 호출해 결과를 변수에 담는다.
    result = get_fruits_info()
    # 계산된 결과를 콘솔에 출력한다.
    print("HashSetExample 실행 결과:", result)


# 현재 파일을 직접 실행했을 때만 메인 함수를 호출한다.
if __name__ == "__main__":
    # 데모 실행을 위해 main()을 호출한다.
    main()
