#결과물 정의
F = open('namefinal.txt', 'w', encoding='utf-8-sig')
'''
SRS = open('namesrs.simplesrs', 'a', encoding='utf-8')
SRS.write('\n')#srs 망가지지 않게
'''
SRS = open('namesrs.simplesrs', 'w', encoding='utf-8')
#자료출처 정의
jp = open('nameJ.txt', 'r', encoding='utf-8')
kr = open('nameK.txt', 'r', encoding='utf-8')
fn = open('namefinal.txt', 'r', encoding='utf-8-sig')

def fndata():
    return "{0}{1}\n".format(jpdata, krdata)
def srsdata():
    return str(fn_name)
name_filter = '0123456789,﻿1,'

#이름 목록 만들기
while True:
    jpdata = jp.readline()
#    jpname = jpdata.strip(''.join(name_filter))
    krdata = kr.readline()
#    krname = krdata.strip(''.join(name_filter))
    if not jpdata: break
    F.write(fndata())
jp.close()
kr.close()
F.close()
while True:
    Fn = fn.readline()
    fn_name = Fn.strip(name_filter)
    if not fn_name: break
    SRS.write(srsdata())
SRS.close()
fn.close()
