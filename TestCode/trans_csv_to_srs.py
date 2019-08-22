"""
결과물을 .csv로도 만들 수 있겠지만 일단 돌아가길래 내버려두도록 하겠습니다.
더 만졌다가 안돌아가면 더 슬플 것 같아서...
"""
#사용 라이브러리
import os
import csv

#원문 추출 파일 및 디렉토리
Jdir = "extractJ/"
Jf = "extractJ.txt"
Jlit = []
OUTJ = open(Jf,'w',encoding='UTF-8-sig') #sig 제거시 BOM 생김

#번역 추출 파일 및 디렉토리
Kdir = "extractK/"
Kf = "extractK.txt"
Klit = []
OUTK = open(Kf,'w', encoding='UTF-8-sig') #sig 제거시 BOM 생김

#디렉토리 파일명 리스트
filenK = os.listdir(Kdir)
filenJ = os.listdir(Jdir)

#스위치 변수 모음
Nullcheck = 0 #최초 명칭 입력시 빈 결과면 0, 아니면 1
R = 0 #csv 내 있는 명칭일 때 1, 아닐때 0
int_info = 0 #자료 내 정수가 있으면 1, 아닐때 0

#정수 제거 필터
name_filter = '0123456789,﻿1,'

#사용자 입력 부분
print("이미 번역된 CSV 파일을 원본 CSV 파일과 대조하여 srs로 만들어주는 프로그램입니다.")
print("chara CSV에서의 기동을 상정하였기에, 타 CSV에서는 오류가 발생할 가능성이 매우 높습니다.\n")
print("원본 파일군은 {0}, 번역 파일군은 {1}에 넣어주세요.\n원본 파일과 번역 파일의 줄이 맞지 않으면 결과물이 이상하게 나옵니다.".format(Jdir,Kdir))
while Nullcheck == 0:
    type_1 = str(input("추출하고 싶은 변수계열 명칭을 입력해주세요. END를 입력하면 종료합니다: ")).upper()
    if type_1 == '':
        print("공란은 입력하실 수 없습니다.")
    else:
        Nullcheck = 1
if type_1 == 'END':
    input("엔터 키를 눌러 종료")
    os._exit(1)

#csv 내 명칭인지 검사
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
            input("대응하는 변수명칭이 없습니다. 엔터 키를 눌러 프로그램을 종료합니다.")
            os._exit(1)
            
# 보여주는 부분
print("\nCSV 추출을 시작합니다.")

#csv 사용 함수
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

#원문csv 추출
for filename in filenJ:
    if ".csv" not in filename:
        continue
    Jfile = Jdir + filename
    with open(Jfile, 'r',encoding='UTF-8-sig',newline='') as csv_in_file:
        for line in Jfile:
            csv_reading(Jlit)

print('\n원문 자료 리스팅 완료!')
listJ = dup_filter(Jlit)
if listJ == []:
    print("\n※원문 자료에 아무것도 잡히지 않았습니다.\n")
else:
    for i in listJ:
        try:
            I = int(i)
            if isinstance(I, int) is True:
                int_info = 1
                continue
        except ValueError:
            OUTJ.write(i)
            OUTJ.write('\n')
    OUTJ.close()
print('원문 txt 파일 작성이 완료되었습니다.')

#번역csv 추출
for filename in filenK:
    if ".csv" not in filename:
        continue
    Kfile = Kdir + filename
    with open(Kfile, 'r',encoding='UTF-8-sig',newline='') as csv_in_file:
        for line in Kfile:
            csv_reading(Klit)
print("\n번역 자료 리스팅 완료!")
listK = dup_filter(Klit)
if listK == []:
    print("\n※번역 자료에 아무것도 잡히지 않았습니다.\n")
else:
    for i in listK:
        try:
            I = int(i)
            if isinstance(I, int) is True:
                int_info = 1
                continue
        except ValueError:
            OUTK.write(i)
            OUTK.write('\n')
    OUTK.close()
print("번역본 txt 파일 작성이 완료되었습니다.\n")
if int_info == 1:
    print('\n※숫자형 자료가 감지되었습니다. 결과물로 나타나지 않습니다.\n')
open("CSVfnclist.csv").close()

#목록 추출 완료메세지
print("CSV 자료 목록의 추출이 완료되었습니다. 종료하시려면 END를 임력하세요.")
print("다음으로 넘어가기 전에 텍스트 파일의 이상 여부를 확인해주세요.\n")
middle_input = input(str("srs 추출로 진행하시려면 엔터: ")).upper()
if middle_input == 'END':
    os._exit(1)

#srs 변환기
    
#최종 결과 파일
Fntxt = open('finaltext.txt','w',encoding='utf-8-sig')
SRS = open('finalsrs.simplesrs','a',encoding='utf-8')

print("\nCSV 추출 자료를 srs 양식에 맞게 추출합니다.\n추출된 자료는 finalsrs.simplesrs의 아랫줄부터 추가됩니다.")
print("자료 수정시 {0} 또는 {1}의 데이터를 우선합니다.".format(Jf,Kf))

#최초인 경우 srs 기초 작성
first_srs = input("\nsrs 파일이 폴더 내에 없다면 1, 있으면 0을 눌러주세요. 타 입력은 0으로 간주합니다: ")
try:
    INT_first = int(first_srs)
    if INT_first == 1:
        first_srs = INT_first
    else:
        first_srs = 0
except ValueError:
    first_srs = 0
if first_srs == 1:
    print("srs 기본 정보(TRIM과 SORT)를 작성합니다. 추가 수정은 변환 완료 후 직접 진행해주세요.")
    SRS.write("[-TRIM-][-SORT-]")
    input("\n엔터를 누르시면 진행됩니다.")

#srs 변환 사용 함수
def FNdata(JDATA,KDATA):
    return "{0}{1}\n".format(JDATA, KDATA)
def readfile(filename_1,filename_2):
    OPEN_1 = open(filename_1, 'r', encoding='utf-8')
    OPEN_2 = open(filename_2, 'r', encoding='utf-8')
    while True:
        DATA_1 = OPEN_1.readline()
        DATA_2 = OPEN_2.readline()
        if int_info == 1:
            DATA_1 = DATA_1.strip(name_filter)
            DATA_2 = DATA_2.strip(name_filter)
        Fntxt.write(FNdata(DATA_1,DATA_2))
        SRS.write(FNdata(DATA_1,DATA_2))
        if not DATA_1: break
    OPEN_1.close()
    OPEN_2.close()
#본문
SRS.write('\n;이하 {0}\n\n'.format(type_1))
readfile(Jf,Kf)
SRS.close()
Fntxt.close()
#결과
print('\n완료!')
input("엔터 키를 눌러 종료합니다")
quit
    
