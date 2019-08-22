Jf = 'extractJ.txt'
Kf = 'extractK.txt'
#최종 결과 파일
Fntxt = open('finaltext.txt','w',encoding='utf-8-sig')
SRS = open('finalsrs.simplesrs','a',encoding='utf-8')

#srs 변환 클래스
class SrsMaker:
    def __init__(self,name1,name2):
        self.filename_1 = name1
        self.filename_2 = name2
    def FNdata(self,DATA1,DATA2):
        return "{0}{1}\n".format(DATA1, DATA2)
    def readTXT(self):
        OPEN_1 = open(self.filename_1, 'r', encoding='utf-8')
        OPEN_2 = open(self.filename_2, 'r', encoding='utf-8')
        while True:
            DATA_1 = OPEN_1.readline()
            DATA_2 = OPEN_2.readline()
            Fntxt.write(self.FNdata(DATA_1,DATA_2))
            SRS.write(self.FNdata(DATA_1,DATA_2))
            if not DATA_1: break
        OPEN_1.close()
        OPEN_2.close
#본문

SM = SrsMaker(Jf, Kf)
SM.readTXT()
SRS.close()
Fntxt.close()
#결과
print('\n완료!')
input("엔터 키를 눌러 종료합니다")
quit
