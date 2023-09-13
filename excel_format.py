import openpyxl

workbook=openpyxl.load_workbook("/Users/lvangge/Desktop/Copy of result3.xlsx")
data=openpyxl.load_workbook("/Users/lvangge/Desktop/数模国赛/py1/data3.xlsx")
num=[8,57,62,70,74,87,86,95,97,106,116,109,125,134,133,135,146,157,172]


sheet=workbook.active
sheet2=data.active
a=sheet2['C']
lr=sheet2['D']
lv=sheet2['E']
cnt=0
C=sheet['C']
for cell in C:
    if cnt>0:
        cell.value=cnt
    cnt+=1

D=sheet['D']
E=sheet['E']
H=sheet['H']


cnt=0
for cell in H:
    if cnt>0:
        cell.value=4
    cnt+=1

workbook.save('result2a.xlsx')