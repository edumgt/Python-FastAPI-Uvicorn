# PDF 문서를 생성하기 위해 fpdf 라이브러리의 FPDF 클래스를 불러온다.
from fpdf import FPDF

# 새로운 PDF 문서 객체를 생성한다.
pdf = FPDF()
# PDF 문서에 첫 페이지를 추가한다.
pdf.add_page()

# Windows에 설치된 맑은 고딕 폰트를 malgun 이름으로 등록한다.
pdf.add_font("malgun", fname="C:/Windows/Fonts/malgun.ttf", uni=True)
# 기본 글꼴을 등록한 malgun 폰트, 크기 16으로 설정한다.
pdf.set_font("malgun", size=16)

# 첫 번째 한글 문장을 가운데 정렬로 출력한다.
pdf.cell(200, 10, text="Python으로 PDF 만들기 예제", new_x="LMARGIN", new_y="NEXT", align="C")
# 두 번째 한글 문장을 왼쪽 정렬로 출력한다.
pdf.cell(200, 10, text="한글도 잘 출력됩니다!", new_x="LMARGIN", new_y="NEXT", align="L")

# 생성한 PDF를 example_korean.pdf 파일명으로 저장한다.
pdf.output("example_korean.pdf")
# PDF 생성 완료 메시지를 콘솔에 출력한다.
print("PDF 생성 완료!")
