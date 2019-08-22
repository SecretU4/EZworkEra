#사용 라이브러리
import os
import csv

#CSV 이름 추출부
# 보여주는 부분

print("CSV에서 이름을 추출합니다.")

#JPN 이름
Jdir = "CharaJ/"
Jf = "nameJ.txt"
OUTJ = open(Jf,'w',encoding='UTF-8')

#KOR 이름
Kdir = "CharaK/"
Kf = "nameK.txt"
OUTK = open(Kf,'w', encoding='UTF-8')

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
print('번역 이름 추출 완료!')

#srs 변환부
#보여지는 부분
print('CSV에서 추출된 자료를 updateera 양식에 맞게 추출합니다.')

#자료출처 정의
jp = open(Jf, 'r', encoding='utf-8')
kr = open(Kf, 'r', encoding='utf-8')

#결과물 정의
F = open('namefinal.txt', 'w', encoding='utf-8-sig')
SRS = open('namesrs.simplesrs', 'a', encoding='utf-8')
SRS.write('\n;이하 이름\n\n')#자료 추가 용이하게

#함수 정의 및 필터 정리
def fndata():
    return "{0}{1}\n".format(jpdata, krdata)
def srsdata():
    return "{0}{1}\n".format(jpname, krname)
name_filter = '0123456789,﻿1,'

#이름 목록 만들기
while True:
    jpdata = jp.readline()
    jpname = jpdata.strip(name_filter)
    krdata = kr.readline()
    krname = krdata.strip(name_filter)
    if not jpdata: break
    F.write(fndata())
    SRS.write(srsdata())
jp.close()
kr.close()
F.close()
SRS.close()

#완료 부분
print('srs 변환 완료!')
input('종료하시려면 아무 키나 누르세요.')
quit
