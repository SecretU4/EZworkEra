"""프로그램 내에서 사용되는 파일 처리와 관련된 모듈"""

import os
import time
from util import CommonSent
from System.interface import MenuPreset

class LoadFile: # 파일 불러오기 상용구
    def __init__(self, NameDir, EncodeType='UTF-8'):
        self.NameDir = NameDir
        self.EncodeType = EncodeType

    def onlyopen(self): return open(self.NameDir)

    def readwrite(self):
        return open(self.NameDir, 'w', encoding=self.EncodeType, newline='')

    def readonly(self):
        return open(self.NameDir, 'r', encoding=self.EncodeType, newline='')

    def addwrite(self):
        return open(self.NameDir, 'a', encoding=self.EncodeType, newline='')


class DirFilter:
    def __init__(self,dirname):
        self.dirname = dirname

    def dir_exist(self):
        dir_target = self.dir_slash()
        if os.path.isdir(dir_target) == False: os.mkdir(dir_target)
        return dir_target

    def dir_slash(self):
        dir_slashed = list(self.dirname)
        if list(self.dirname) == []: pass
        elif dir_slashed.pop() != '/' and dir_slashed.pop() != '\\':
            self.dir_target = self.dirname + '\\'
        return self.dir_target


class FileFilter:
    def __init__(self,opt_num=0):
        self.option_num = opt_num

    def files_ext(self,dir_target,ext_target):
        ext_target = ext_target.upper()
        self.files = []
        if self.option_num == 0: # 하위 포함
            for (path, _, files) in os.walk(dir_target):
                for filename in files:
                    file_type = os.path.splitext(filename)[-1].upper()
                    if file_type == ext_target:
                        self.files.append('{0}\\{1}'.format(path,filename))
        elif self.option_num == 1: # 해당 디렉토리만
            for filename in os.listdir(dir_target):
                file_type = os.path.splitext(filename)[-1].upper()
                if file_type == ext_target:
                        self.files.append('{0}\\{1}'.format(dir_target,filename))
        return self.files

    def files_name(self,dir_target,name_target):
        name_target = name_target.upper()
        self.files = []
        if self.option_num == 0: # 하위 포함
            for (_, _, files) in os.walk(dir_target):
                for filename in files:
                    FoundName = os.path.split(filename)[-1].upper()
                    if name_target in FoundName:
                        self.files.append(FoundName)
        elif self.option_num == 1: # 해당 디렉토리만
            for filename in os.listdir(dir_target):
                FoundName = os.path.split(filename)[-1].upper()
                if name_target in FoundName:
                    self.files.append(FoundName)
        return self.files

    def sep_filename(self,filename): # 0: 오직 파일명 1: 확장자 제외 2: 상위폴더명 제외
        if self.option_num == 0:
            seprated_filename = os.path.basename(filename)
            seprated_filename = os.path.splitext(seprated_filename)[0]
        elif self.option_num == 1:
            seprated_filename = os.path.splitext(filename)[0]
        elif self.option_num == 2:
            seprated_filename = os.path.split(filename)[-1]
        return seprated_filename

    def search_filename_wordwrap(self,filenames,keyword_list):
        filename_dict = {}
        for filename in filenames:
            filename_dict[FileFilter().sep_filename(filename).upper().split()[0]] = filename
        for keyword in keyword_list:
            if keyword.upper() in list(filename_dict.keys()):
                target_name = filename_dict.get(keyword.upper())
                break
            else: target_name = None
        return target_name

    def get_filelist(self,filetype):
        user_input = CustomInput(filetype)
        target_dir = user_input.input_option(1)
        self.option_num = MenuPreset().yesno("하위폴더까지 포함해 진행하시겠습니까?")
        encode_type = MenuPreset().encode()
        files = self.files_ext(target_dir, '.'+filetype)
        return files,encode_type


class CustomInput: # 사용자의 입력 클래스
    def __init__(self,target):
        self.target = target

    def input_dir(self):
        self.dir_inputed = str(input("{0}이(가) 위치하는 디렉토리명을 입력해주세요.\
 존재하지 않는 디렉토리인 경우 오류가 발생합니다. : ".format(self.target)))
        if len(self.dir_inputed)==0:
            print("특정 디렉토리의 입력 없이 진행합니다. 오류가 발생할 수 있습니다.")
            self.dir_inputed = '.'
            time.sleep(1)
        self.dir_inputed = DirFilter(self.dir_inputed).dir_slash()

    def input_name(self):
        while True:
            self.name_inputed = str(input("{0}의 명칭을 입력해주세요. : ".format(self.target)))
            if len(self.name_inputed) == 0:
                CommonSent.no_void()
                continue
            break

    def input_type(self):
        while True:
            self.type_inputed = str(input("{0}의 타입을 입력해주세요. : ".format(self.target))).upper()
            if len(self.type_inputed) == 0:
                CommonSent.no_void()
                continue
            break

    def input_option(self,option_num): # 0: 모두, 1: 디렉토리, 2: 이름, 3: 이름/타입
        if option_num == 0:
            self.input_dir()
            self.input_name()
            self.input_type()
            return self.dir_inputed,self.name_inputed,self.type_inputed
        elif option_num == 1:
            self.input_dir()
            return self.dir_inputed
        elif option_num == 2:
            self.input_name()
            return self.name_inputed
        elif option_num == 3:
            self.input_name()
            self.input_type()
            return self.name_inputed,self.input_type
