"""
결과물을 .csv로도 만들 수 있겠지만 일단 돌아가길래 내버려두도록 하겠습니다.
더 만졌다가 안돌아가면 더 슬플 것 같아서...
"""
#사용 라이브러리
import os
import csv

#사용자 입력 부분
print("이미 번역된 CSV 파일을 원본 CSV 파일과 대조하여 srs로 만들어주는 프로그램입니다.")
print("chara CSV에서의 기동을 상정하였기에, 타 CSV에서는 오류가 발생하기 매우 쉽습니다.\n")
print("원본 파일은 extractJ, 번역 파일은 extractK에 넣어주세요.원본 파일과 번역 파일의 줄이 맞지 않으면 결과물이 이상하게 나옵니다.")
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

#JPN
Jdir = "extractJ/"
Jset = set()
Jf = "extractJ.txt"
OUTJ = open(Jf,'w',encoding='UTF-8-sig') #sig 제거시 BOM 생김

#KOR
Kdir = "extractK/"
Kf = "extractK.txt"
Kset = set()
OUTK = open(Kf,'w', encoding='UTF-8-sig') #sig 제거시 BOM 생김

#디렉토리 파일명 리스트
filenK = os.listdir(Kdir)
filenJ = os.listdir(Jdir)

#Jname
for filename in filenJ:
    if ".csv" not in filename:
        continue
    Jfile = Jdir + filename
    with open(Jfile, 'r',encoding='UTF-8-sig',newline='') as csv_in_file:
        for line in Jfile:
            csv_read = csv.reader(csv_in_file)
            for row_list in csv_read:
                try:
                    FnCall = str(row_list[0]).strip()
                    data_type = str(row_list[1]).strip()
                except IndexError:
                    continue
                if FnCall == type_1a or FnCall == type_1b:
                    Jset.add(data_type)
                else:
                    continue
print('원문 자료 추출 완료!')
listJ = list(Jset)
for i in listJ:
    OUTJ.write(i)
    OUTJ.write('\n')
OUTJ.close()
print(type(listJ[1]))

#Kname
for filename in filenK:
    if ".csv" not in filename:
        continue
    Kfile = Kdir + filename
    with open(Kfile, 'r',encoding='UTF-8-sig',newline='') as csv_in_file:
        for line in Kfile:
            csv_read = csv.reader(csv_in_file)
            for row_list in csv_read:
                try:
                    FnCall = str(row_list[0]).strip()
                    data_type = str(row_list[1]).strip()
                except IndexError:
                    continue
                if FnCall == type_1a or FnCall == type_1b:
                    Kset.add(data_type)
                else:
                    continue
listK = list(Kset)
for i in listK:
    OUTK.write(i)
    OUTK.write('\n')
print(type(listK[1]))

#열린 파일 정리
OUTJ.close()
OUTK.close()
#완료메세지
print("완료!")
input("아무 키를 눌러 종료하세요")
quit
