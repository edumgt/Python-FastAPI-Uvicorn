# 한글(HWP) COM 자동화를 위해 win32com client 모듈을 불러온다.
import win32com.client as win32
# 저장 경로를 절대 경로로 계산하기 위해 os 모듈을 불러온다.
import os

# 한글 프로그램 COM 객체를 생성(또는 재사용)한다.
hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")
# 새 HWP 문서를 새 창 탭 옵션(False)으로 생성한다.
hwp.XHwpDocuments.Add(False)

# 텍스트 삽입 액션의 기본 파라미터 세트를 준비한다.
hwp.HAction.GetDefault("InsertText", hwp.HParameterSet.HInsertText.HSet)
# 삽입할 본문 텍스트를 파라미터 세트에 지정한다.
hwp.HParameterSet.HInsertText.Text = "안녕하세요, Python에서 생성한 HWP 문서입니다!"
# 설정한 텍스트 삽입 액션을 실제로 실행한다.
hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)

# 저장 파일명을 기준으로 절대 경로를 계산한다.
save_path = os.path.abspath("python_hwp_example.hwp")
# 현재 문서를 계산된 경로에 저장한다.
hwp.SaveAs(save_path)

# 한글 프로그램 객체를 정상 종료한다.
hwp.Quit()
# 저장 완료 경로를 포함한 메시지를 출력한다.
print(f"HWP 문서 생성 완료: {save_path}")
