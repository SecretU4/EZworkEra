# CSV 정보 추출 코드 (클래스 기반)

# 사용 라이브러리
import os
import csv

# 클래스 목록
## 파일 관련 입력 정보 클래스
class File:
    PresetOn = 0
    def __init__(self, Dir, Name, Type):
        self.Dir = Dir
        self.Name = Name
        self.Type = Type
    def SetPreset(self):
        self.DirName = self.Dir + self.Name + '.' + self.Type
        self.FullName = self.Name + '.' + self.Type
        self.PresetOn = 1
## 파일 불러오기 클래스
class Load:
    def __init__(self, NameDir):
        self.NameDir = NameDir
    def readwrite(self):
        open(self.NameDir, 'w', encoding='UTF-8=sig', newline='')
    def readonly(self):
        open(self.NameDir, 'r', encoding='UTF-8-sig', newline='')
    def addwrite(self):
        open(self.NameDir, 'a', encoding='UTF-8-sig', newline='')
    def ListCSV(self, info1, info2):
        pass
    def CharaCSV(self, info1, info2):
        pass
    def OtherCSV(self, number, info1):
        pass
    
# 사용자 입력 부분
inputDir = str(input("파일이 위치하는 폴더명을 입력해주세요. : "))
if inputDir.find('/')!=len(inputDir)-1:
    inputDir = inputDir + '/'
inputName = str(input("파일의 이름을 입력해주세요. : "))
inputType = str(input("파일의 타입을 입력해주세요. 현재 CSV 타입만 지원합니다.: ")).upper()
if inputType != 'CSV':
    print("안된다니까요")
InputA = File(inputDir, inputName, inputType)
InputA.SetPreset()
print("여기까진 됨")
if InputA.PresetOn == 1:
    print(InputA.DirName)
    print("it was true")
elif InputA.PresetOn == 0:
    print("프리셋 처리 안됨")