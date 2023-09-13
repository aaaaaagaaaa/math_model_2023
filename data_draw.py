import openpyxl
workbook=openpyxl.load_workbook(path1)
sheet=workbook.active

x=[cell.value for cell in sheet['A']]
y=[cell.value for cell in sheet['B']]
x.pop(0)
y.pop(0)