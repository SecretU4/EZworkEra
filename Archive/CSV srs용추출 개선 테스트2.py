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
    type_1 = str(input("추출하고 싶은 변수계열 명칭을 입력해주세요. END를 입력하면 종료합니다: ")).upper()
    if type_1 == '':
        print("공란은 입력하실 수 없습니다.")
    else:
        Nullcheck = 1
if type_1 == 'END':
    input("아무 키나 눌러 종료")
    os._exit(1)

#CSV 명칭인지 검사
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
            if type_1 == JFn or type_1 == EFn:
                typeJ = JFn
                typeE = EFn
                R = 1
                break
        if R == 0:
            open("CSVfnclist.csv").close()
            input("대응하는 변수명칭이 없습니다. 아무 키를 눌러 프로그램을 종료합니다.")
            os._exit(1)
            
# 보여주는 부분
print("CSV에서 자료를 추출합니다.")

#JPN
Jdir = "extractJ/"
Jf = "extractJ.txt"
Jlit = []
OUTJ = open(Jf,'w',encoding='UTF-8-sig') #sig 제거시 BOM 생김

#KOR
Kdir = "extractK/"
Kf = "extractK.txt"
Klit = []
OUTK = open(Kf,'w', encoding='UTF-8-sig') #sig 제거시 BOM 생김

int_info = 0
#디렉토리 파일명 리스트
filenK = os.listdir(Kdir)
filenJ = os.listdir(Jdir)

#사용된 함수 정의
def csv_reading(list_name): #CSV 1열 조건 확인 후 2열 출력
    csv_read = csv.reader(csv_in_file)
    for row_list in csv_read:
        try:
            FnCall = str(row_list[0]).strip()
            data_type = row_list[1].strip()
        except IndexError:
            continue
        if FnCall == typeJ or FnCall == typeE:
            list_name.append(data_type)
        else:
            continue
    return list_name

def dup_filter(list_name): #중복 감별 들어온 순서대로 저장
    Flit = []
    set_filter = set()
    for e in list_name:
        if e not in set_filter:
            Flit.append(e)
            set_filter.add(e)
    return Flit

#JPSET
for filename in filenJ:
    if ".csv" not in filename:
        continue
    Jfile = Jdir + filename
    with open(Jfile, 'r',encoding='UTF-8-sig',newline='') as csv_in_file:
        for line in Jfile:
            csv_reading(Jlit)

print('원문 자료 추출 완료!')
listJ = dup_filter(Jlit)
if listJ == []:
    print("번역 자료에 아무것도 잡히지 않았습니다.")
else:
    for i in listJ:
        if isinstance(i, int) is True:
            int_info = 1
        else:
            OUTJ.write(i)
            OUTJ.write('\n')
    OUTJ.close()

#KRSET
for filename in filenK:
    if ".csv" not in filename:
        continue
    Kfile = Kdir + filename
    with open(Kfile, 'r',encoding='UTF-8-sig',newline='') as csv_in_file:
        for line in Kfile:
            csv_reading(Klit)
listK = dup_filter(Klit)
if listK == []:
    print("번역 자료에 아무것도 잡히지 않았습니다.")
else:
    for i in listK:
        if isinstance(i, int) is True:
            int_info = 1
        else:
            OUTK.write(i)
            OUTK.write('\n')
    OUTK.close()
print("번역 자료 추출 완료!")
if int_info == 1:
    print('숫자형 자료가 감지되었습니다.')
open("CSVfnclist.csv").close()
#완료메세지
input("아무 키를 눌러 종료하세요")
quit
