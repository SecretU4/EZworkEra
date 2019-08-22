"""
결과물을 .csv로도 만들 수 있겠지만 일단 돌아가길래 내버려두도록 하겠습니다.
더 만졌다가 안돌아가면 더 슬플 것 같아서...
"""
#사용 라이브러리
import os
import csv

# 보여주는 부분
print("CSV에서 이름을 추출합니다.")

#JPN 이름
Jdir = "CharaJ/"
Jf = "nameJ.txt"
OUTJ = open(Jf,'w',encoding='UTF-8-sig') #sig 제거시 BOM 생김

#KOR 이름
Kdir = "CharaK/"
Kf = "nameK.txt"
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
                    N = str(row_list[1]).strip()
                    A = str(row_list[0]).strip()
                except IndexError:
                    continue
                if A == "番号" or A == "NO":
                    OUTJ.write(N)
                    OUTJ.write(",")
                elif A == "名前" or A == "NAME":
                    OUTJ.write(N)
                    OUTJ.write("\n")
                else:
                    continue
print('원본 이름 추출 완료!')

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
                    N = str(row_list[1]).strip()
                    A = str(row_list[0]).strip()
                except IndexError:
                    continue
                if A == "番号" or A == "NO":
                    OUTK.write(N)
                    OUTK.write(",")
                elif A == "名前" or A == "NAME":
                    OUTK.write(N)
                    OUTK.write("\n")
                else:
                    continue
#열린 파일 정리
OUTJ.close()
OUTK.close()

#완료메세지
print("완료!")
input("아무 키를 눌러 종료하세요")
quit
