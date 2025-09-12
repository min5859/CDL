import win32com.client as win32
import pandas as pd

# Excel 애플리케이션 열기
excel = win32.Dispatch("Excel.Application")
excel.Visible = False  # 엑셀 창을 숨김

# 보안 걸린 엑셀 파일 열기
file_path = 'path_to_your_protected_excel.xlsx'
password = 'your_password'
workbook = excel.Workbooks.Open(file_path, False, False, None, password)

# 첫 번째 시트를 선택하여 읽음
sheet = workbook.Sheets(1)

# 시트의 사용 범위를 가져옴
used_range = sheet.UsedRange

# 데이터를 리스트로 변환
data = used_range.Value

# 엑셀 파일 닫기
workbook.Close(SaveChanges=False)
excel.Quit()

# 데이터를 pandas DataFrame으로 변환
df = pd.DataFrame(data[1:], columns=data[0])  # 첫 번째 행을 헤더로 사용

print(df)
