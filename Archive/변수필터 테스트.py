#사용 라이브러리
import os
import csv

#사용자 입력 부분
print("이미 번역된 CSV 파일을 원본 CSV 파일과 대조하여 srs로 만들어주는 프로그램입니다.")
print("chara CSV에서의 기동을 상정하였기에, 타 CSV에서는 오류가 발생하기 매우 쉽습니다.\n")
Nullcheck = 0
while Nullcheck == 0:
    type_1a = str(input("추출하고 싶은 변수계열 명칭을 입력해주세요. END를 입력하면 종료합니다: ")).upper()
    if type_1a == '':
        print("공란은 입력하실 수 없습니다.")
    else:
        Nullcheck = 1
if type_1a == 'END':
    input("아무 키나 눌러 종료")
    os._exit(1)

type_1b = str(input("추출하고 싶은 변수계열의 다른 명칭이 있다면 입력해주세요: ")).upper()
R = 0
with open("CSVfnclist.csv", 'r',encoding='UTF-8-sig',newline='') as csv_in_file:
    for line in "CSVfnclist.csv":
        csv_read = csv.reader(csv_in_file)
        for row_list in csv_read:
            try:
                JFn = str(row_list[0]).strip()
                EFn = str(row_list[1]).strip()
            except IndexError:
                continue
            if [JFn,EFn] == [type_1a, type_1b] or [EFn, JFn] == [type_1a, type_1b]:
                R = 1
                break
            elif len(type_1b) == 0:
                if type_1a == JFn or type_1a == EFn:
                    R = 1
                    break
        if R == 0:
            open("CSVfnclist.csv").close()
            input("대응하는 변수명칭이 없습니다. 아무 키를 눌러 프로그램을 종료합니다.")
            os._exit(1)
open("CSVfnclist.csv").close()
            
# 보여주는 부분
print("CSV에서 자료를 추출합니다.")
