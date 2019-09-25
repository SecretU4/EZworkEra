# CSV 정보 추출 코드 (클래스 기반)
# 사용 라이브러리
import os
import csv
# 클래스 목록
## 파일 관련 입력 정보 클래스
class FileInfo:
    PresetOn = 0 # preset 사용여부 판별
    def __init__(self, Dir, Name, Type):
        self.Dir = Dir
        self.Name = Name
        self.Type = Type
    def SetPreset(self):
        self.DirName = self.Dir + self.Name + '.' + self.Type
        self.FullName = self.Name + '.' + self.Type
        self.PresetOn = 1
## 각종 정보 필터 클래스
class DataFilter:
    def DirSlash(self, Dir):
        Filter_DirSlash = list(Dir)
        if list(Dir) == []: pass
        elif Filter_DirSlash.pop() != "/":
            Dir = Dir + "/"
        return Dir
## 파일 불러오기 클래스
class LoadFile:
    def __init__(self, NameDir):
        self.NameDir = NameDir
    def onlyopen(self):
        open(self.NameDir)
    def readwrite(self):
        open(self.NameDir, 'w', encoding='UTF-8=sig', newline='')
    def readonly(self):
        open(self.NameDir, 'r', encoding='UTF-8-sig', newline='')
    def addwrite(self):
        open(self.NameDir, 'a', encoding='UTF-8-sig', newline='')
class CSVLoad(LoadFile):
    def ListCSV(self, info1, info2):
        pass
    def CharaCSV(self, info1, info2):
        pass
    def OtherCSV(self, number, info1):
        pass
class ERBLoad(LoadFile):
    pass
# 사용자 입력 부분
inputDir = str(input("파일이 위치하는 폴더명을 입력해주세요. \
존재하지 않는 폴더명인 경우 오류가 발생합니다.: "))
if len(inputDir)==0:
    print("특정 디렉토리의 입력 없이 진행합니다.")
inputDir = DataFilter().DirSlash(inputDir)
while True:
    inputName = str(input("파일의 이름을 입력해주세요. : "))
    if len(inputName) == 0:
        print("공란은 입력하실 수 없습니다.")
        continue
    break
while True:
    inputType = str(input("파일의 타입을 입력해주세요. 현재 CSV 타입만 지원합니다.: ")).upper()
    if len(inputType) == 0:
        print("공란은 입력하실 수 없습니다.")
        continue
    elif inputType == 'CSV': print("땡큐!")
    else: print("안돼도 모릅니다.")
    break
InputA = FileInfo(inputDir, inputName, inputType)
InputA.SetPreset()
if InputA.PresetOn == 1:
    print("체크 해냈다!")
elif InputA.PresetOn == 0:
    print("슈벌")
print(InputA.DirName)
TestA = FileInfo('TestDir', 'TestNam', 'TestTyp')
print(TestA.PresetOn)