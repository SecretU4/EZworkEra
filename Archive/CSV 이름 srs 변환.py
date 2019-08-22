#보여지는 부분
print('CSV에서 추출된 자료를 updateera 양식에 맞게 추출합니다.')

#자료출처 정의
jp = open('nameJ.txt', 'r', encoding='utf-8')
kr = open('nameK.txt', 'r', encoding='utf-8')

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
print('완료!')
input('종료하시려면 아무 키나 누르세요.')
quit
