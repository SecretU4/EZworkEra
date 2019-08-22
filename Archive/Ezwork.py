#자료출처 정의
jp = open('jpname.txt', 'r', encoding='utf-8')
kr = open('krname.txt', 'r', encoding='utf-8')
#결과물 정의
F = open('final.txt', 'w', encoding='utf-8')
def fndata():
    return "{0}{1}\n".format(jpdata, krdata)
#본문
while True:
    jpdata = jp.readline()
    krdata = kr.readline()
    if not jpdata: break
    F.write(fndata())
jp.close()
kr.close()
F.close()
