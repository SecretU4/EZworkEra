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
    def DirSlash(self, Directory):
        Filter_DirSlash = list(Directory)
        if list(Directory) == []: pass
        elif Filter_DirSlash.pop() != "/": Directory = Directory + "/"
        return Directory
    def Dup_Filter(self, list_name): #중복 감별 들어온 순서대로 저장
        Flitered_list = []
        set_filter = set()
        for data in list_name:
            if data not in set_filter:
                Flitered_list.append(data)
                set_filter.add(data)
        return Flitered_list
## 파일 불러오기 클래스
class LoadFile:
    def __init__(self, NameDir):
        self.NameDir = NameDir
    def onlyopen(self): return open(self.NameDir)
    def readwrite(self):
        return open(self.NameDir, 'w', encoding='UTF-8-sig', newline='')
    def readonly(self):
        return open(self.NameDir, 'r', encoding='UTF-8-sig', newline='')
    def addwrite(self):
        return open(self.NameDir, 'a', encoding='UTF-8-sig', newline='')
class CSVLoad(LoadFile):
    def ReadCSV(self):
        self.CSVRead = csv.reader(self.readonly())
    def OutFileName(self, Out_File_Name):
        self.OUTFile = Out_File_Name
    def CharaCSV(self):
        for row_list in self.CSVRead:
            try:
                self.First_data = eval(row_list[0]).strip()
                self.Second_data = str(row_list[1]).strip()
            except IndexError: continue
            if self.First_data == "番号" or self.First_data == "NO":
                    self.onlyopen(self.OUTFile).write(self.Second_data)
                    self.onlyopen(self.OUTFile).write(",")
            elif self.First_data == "名前" or self.First_data == "NAME":
                    self.onlyopen(self.OUTFile).write(self.Second_data)
                    self.onlyopen(self.OUTFile).write("\n")
            else: continue
    def OtherCSV(self, info1):
        pass
    def AllCSV(self,info1,info2):
        pass
class ERBLoad(LoadFile):
    pass
# 사용자 입력 클래스
class Custom_input:
    def File_input(self):
        self.inputDir = str(input("파일이 위치하는 폴더명을 입력해주세요.\
 존재하지 않는 폴더명인 경우 오류가 발생합니다.: "))
        if len(self.inputDir)==0:
            print("특정 디렉토리의 입력 없이 진행합니다.")
        self.inputDir = DataFilter().DirSlash(self.inputDir)
        while True:
            self.inputName = str(input("파일의 이름을 입력해주세요.: "))
            if len(self.inputName) == 0:
                print("공란은 입력하실 수 없습니다.")
                continue
            break
        while True:
            self.inputType = str(input("파일의 타입을 입력해주세요.: ")).upper()
            if len(self.inputType) == 0:
                print("공란은 입력하실 수 없습니다.")
                continue
            break
    def File_Results(self):
        return self.inputDir,self.inputName,self.inputType
# 기능 묶음 클래스
class Organized_func:
    def Opening_File(self):
        OrgA = Custom_input() # 자료 입력받음
        OrgA.File_input()
        OrgA_Dir,OrgA_Name,OrgA_Type = OrgA.File_Results()
        self.OrgA_Final = FileInfo(OrgA_Dir,OrgA_Name,OrgA_Type)
        self.OrgA_Final.SetPreset()
        return self.OrgA_Final
# 디버그용 코드
if __name__ == "__main__":
    # Custom_input과 Fileinfo 클라스 테스트코드
    '''
    Test = Custom_input()
    Test.File_input()
    print(Test.File_Results())
    TD, TN, TT = Test.File_Results()
    InfoTest = FileInfo(TD,TN,TT)
    InfoTest.SetPreset()
    print(InfoTest.PresetOn,InfoTest.DirName)
    '''
    # LoadFile 클라스 테스트코드
    '''
    TestA = LoadFile('test.txt')
    ResultA = TestA.readwrite()
    print(ResultA)
    ResultA.write("쉬이이벌")
    ResultA.close
    '''
    # CSVLoad 클라스 테스트코드
    '''
    PreTest = FileInfo('Airang/Butter/','Egg','csv')
    print(PreTest.PresetOn,PreTest.Dir)
    CSVTest = CSVLoad("test.csv")
    '''
