# EZworkEra 메인 모듈
# 사용 라이브러리
import os
# 클래스 목록
## 사용자 화면 관련
### 관용구
class Common_Sent:
    def NotOK(self): print("유효하지 않은 입력입니다.")
    def EndComment(self):
        print("이용해주셔서 감사합니다.")
        input("엔터를 누르면 종료됩니다.")
### 메인 메뉴
class Main_Menu:
    def Print_MainMenu(self):
        print("""
        [1]. CSV 파일 처리
        [2]. ERB 파일 처리 (미실장)
        [3]. ERH 파일 처리 (미실장)
        [4]. 프로그램 종료
        """)
        self.MenuSelect = input("번호를 입력하세요. 클릭은 지원하지 않습니다.:")
    def Run_MainMenu(self):
        AllowNum = (1,2,3,4)
        while True:
            self.Print_MainMenu()
            if AllowNum.count(self.MenuSelect) == True:
                return self.MenuSelect
            elif self.MenuSelect == '99' or self.MenuSelect == '999':
                print("디버그 기능 없습니다!")
            else: Common_Sent().NotOK()
### 사용자의 입력 클래스
class Custom_input:
    def __init__(self,Target):
        self.Target = Target
    def Dir_Input(self):
        self.inputDir = str(input("{0}이(가) 위치하는 디렉토리명을 입력해주세요.\
 존재하지 않는 디렉토리인 경우 오류가 발생합니다.: ".format(self.Target)))
        if len(self.inputDir)==0:
            print("특정 디렉토리의 입력 없이 진행합니다.")
        self.inputDir = DataFilter().DirSlash(self.inputDir)
    def Name_input(self):
        while True:
            self.inputName = str(input("{0}의 명칭을 입력해주세요.: ".format(self.Target)))
            if len(self.inputName) == 0:
                print("공란은 입력하실 수 없습니다.")
                continue
            break
    def Type_input(self):
        while True:
            self.inputType = str(input("{0}의 타입을 입력해주세요.: ".format(self.Target))).upper()
            if len(self.inputType) == 0:
                print("공란은 입력하실 수 없습니다.")
                continue
            break
    def InputOption(self,OptionNum): # 0: 모두, 1: 디렉토리, 2: 이름, 3: 이름/타입
        if OptionNum == 0:
            self.Dir_Input()
            self.Name_input()
            self.Type_input()
            return self.inputDir,self.inputName,self.inputType
        elif OptionNum == 1:
            self.Dir_Input()
            return self.inputDir
        elif OptionNum == 2:
            self.Name_input()
            return self.inputName
        elif OptionNum == 3:
            self.Name_input()
            self.Type_input()
            return self.inputName,self.Type_input
class Encode:
    def Encode_input(self):
        while True:
            print("[1]. UTF-8\n[2]. UTF-8-BOM\n[3]. SHIFT-JIS\n[4]. EUC-KR")
            EncType = input("처리할 파일의 인코딩 타입에 해당하는 번호를 입력하세요. :")
            if EncType == '1':
                EncType = 'UTF-8-SIG'
                break
            elif EncType == '2':
                EncType = 'UTF-8'
                break
            elif EncType == '3':
                EncType = 'SHIFT=JIS'
                break
            elif EncType == '4':
                EncType = 'EUC-KR'
                break
            else:
                Common_Sent().NotOK()
        return EncType
## 내부 기초기능 관련
### 파일 관련 정보 클래스
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
### 각종 정보 필터 클래스
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
### 파일 불러오기 클래스
class LoadFile:
    def __init__(self, NameDir, EncodeType):
        self.NameDir = NameDir
        self.EncodType = EncodeType
    def onlyopen(self): return open(self.NameDir)
    def readwrite(self):
        return open(self.NameDir, 'w', encoding=self.EncodType, newline='')
    def readonly(self):
        return open(self.NameDir, 'r', newline='')
    def addwrite(self):
        return open(self.NameDir, 'a', encoding=self.EncodType, newline='')
### 디렉토리 내 특정 확장자 파일 검색
class Find_File_in_Dir:
    def FileList_Ext(self,TargetDir,TargetExt):
        TargetExt = TargetExt.upper()
        self.FileList = []
        for (path, dir, files) in os.walk(TargetDir):
            for filename in files:
                FileType = os.path.splitext(filename)[-1].upper()
                if FileType == TargetExt:
                    self.FileList.append('{0}/{1}'.format(path,filename))
        return self.FileList
    def FileList_Name(self,TargetDir,TargetName):
        TargetName = TargetName.upper()
        self.FileList = []
        for (path, dir, files) in os.walk(TargetDir):
            for filename in files:
                FoundName = os.path.split(filename)[-1].upper()
                if TargetName in FoundName:
                    self.FileList.append(FoundName)
        return self.FileList
# 디버그용 코드
if __name__ == "__main__":
    pass
