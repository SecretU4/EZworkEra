"""프로그램 내에서 사용되는 파일 처리와 관련된 모듈

Classes:
    LoadFile
    DirFilter
    FileFilter
    CustomInput
"""

import os
import time
from util import CommonSent
from System.interface import MenuPreset

class LoadFile:
    """파일을 불러오는 데 사용하는 클래스. 기본 함수인 open을 양식화함.\n
    디랙토리+파일명, 인코딩(기본값 UTF-8)을 필요로 함.

    Functions:
        onlyopen()
        readwrite()
        readonly()
        addwrite()
    """
    def __init__(self, NameDir, EncodeType='UTF-8'):
        self.NameDir = NameDir
        self.EncodeType = EncodeType

    def onlyopen(self):
        """open과 본질적으로 같음."""
        return open(self.NameDir)

    def readwrite(self):
        """처음부터 쓰기"""
        return open(self.NameDir, 'w', encoding=self.EncodeType, newline='')

    def readonly(self):
        """읽기 전용"""
        return open(self.NameDir, 'r', encoding=self.EncodeType, newline='')

    def addwrite(self):
        """있던 내용 뒤에 추가해 쓰기"""
        return open(self.NameDir, 'a', encoding=self.EncodeType, newline='')


class DirFilter:
    """디렉토리명 관련 필터링 클래스.\n
    클래스 호출시 디렉토리명 입력 필수. 처리된 명칭은 return됨.

    Functions:
        dir_exist()
        dir_slash()
    """
    def __init__(self,dirname):
        self.dirname = dirname

    def dir_exist(self):
        """해당 디렉토리의 존재 여부 판별"""
        dir_target = self.dir_slash()
        if os.path.isdir(dir_target) == False: os.mkdir(dir_target)
        return dir_target

    def dir_slash(self):
        """디렉토리명의 맨 끝에 \\나 / 기호를 붙임."""
        dir_slashed = list(self.dirname)
        if list(self.dirname) == []: pass
        elif dir_slashed.pop() != '/' and dir_slashed.pop() != '\\':
            self.dir_target = self.dirname + '\\'
        return self.dir_target


class FileFilter:
    """ 파일 목록이나 특정 파일명의 처리와 관련된 클래스.\n
    클래스 호출시 입력 인자는 특정 함수에 대응하는 설정 번호(기본값 0).

    Functions:
        files_ext(dir,ext)
        files_name(dir,name)
        sep_filename(name)
        search_filename_wordwrap(names,kwaglist)
        get_filelist(ext)
    """
    def __init__(self,opt_num=0):
        self.option_num = opt_num

    def files_ext(self,dir_target,ext_target):
        """특정 디렉토리 내 해당 확장자 파일의 목록을 불러옴.

        옵션 번호:
            0: 하위폴더 포함
            1: 하위폴더 미포함
        """
        ext_target = ext_target.upper()
        self.files = []
        if self.option_num == 0:
            for (path, _, files) in os.walk(dir_target):
                for filename in files:
                    file_type = os.path.splitext(filename)[-1].upper()
                    if file_type == ext_target:
                        self.files.append('{0}\\{1}'.format(path,filename))
        elif self.option_num == 1:
            for filename in os.listdir(dir_target):
                file_type = os.path.splitext(filename)[-1].upper()
                if file_type == ext_target:
                        self.files.append('{0}\\{1}'.format(dir_target,filename))
        return self.files

    def files_name(self,dir_target,name_target):
        """특정 디렉토리 내 해당 이름이 포함된 파일의 목록을 불러옴.

        옵션 번호:
            0: 하위폴더 포함
            1: 하위폴더 미포함
        """
        name_target = name_target.upper()
        self.files = []
        if self.option_num == 0:
            for (_, _, files) in os.walk(dir_target):
                for filename in files:
                    FoundName = os.path.split(filename)[-1].upper()
                    if name_target in FoundName:
                        self.files.append(FoundName)
        elif self.option_num == 1:
            for filename in os.listdir(dir_target):
                FoundName = os.path.split(filename)[-1].upper()
                if name_target in FoundName:
                    self.files.append(FoundName)
        return self.files

    def sep_filename(self,filename):
        """입력받은 파일명(문자열)을 처리하는 함수.

        옵션 번호:
            0: 파일명'만' 떼어냄
            1: 확장자를 떼어냄
            2: 상위 폴더명을 제외함
        example: origin = 'chara/char001/reimu.erb'\n
            opt0='reimu'
            opt1='chara/char001/reimu'
            opt2:'reimu.erb'
        """
        if self.option_num == 0:
            seprated_filename = os.path.basename(filename)
            seprated_filename = os.path.splitext(seprated_filename)[0]
        elif self.option_num == 1:
            seprated_filename = os.path.splitext(filename)[0]
        elif self.option_num == 2:
            seprated_filename = os.path.split(filename)[-1]
        return seprated_filename

    def search_filename_wordwrap(self,filenames,keyword_list):
        """파일 목록 안에서 입력된 키워드 목록에 정확히 일치하는 파일명만 뽑음\n
        처음으로 매치되는 키워드/파일명만 return함."""
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
        """Ctrltool의 Func 클래스들이 사용하는 파일 목록 입력 양식 함수.\n
        입력 인자는 파일 목록화할 확장자."""
        user_input = CustomInput(filetype)
        target_dir = user_input.input_option(1)
        self.option_num = MenuPreset().yesno("하위폴더까지 포함해 진행하시겠습니까?")
        encode_type = MenuPreset().encode()
        files = self.files_ext(target_dir, '.'+filetype)
        return files,encode_type


class CustomInput:
    """사용자의 파일 관련 입력 부분 처리 클래스.\n
    필요 인자는 절차 중 표시되는 대상의 명칭임.

    Functions:
        input_option(num)

    Variables:
        dir_inputed
        name_inputed
        type_inputed
    """
    def __init__(self,target):
        self.target = target

    def __input_dir(self):
        self.dir_inputed = str(input("{0}이(가) 위치하는 디렉토리명을 입력해주세요.\
 존재하지 않는 디렉토리인 경우 오류가 발생합니다. : ".format(self.target)))
        if len(self.dir_inputed)==0:
            print("특정 디렉토리의 입력 없이 Root 디렉토리로 진행합니다. 오류가 발생할 수 있습니다.")
            self.dir_inputed = '.'
            time.sleep(1)
        self.dir_inputed = DirFilter(self.dir_inputed).dir_slash()

    def __input_name(self):
        while True:
            self.name_inputed = str(input("{0}의 명칭을 입력해주세요. : ".format(self.target)))
            if len(self.name_inputed) == 0:
                CommonSent.no_void()
                continue
            break

    def __input_type(self):
        while True:
            self.type_inputed = str(input("{0}의 타입을 입력해주세요. : ".format(self.target))).upper()
            if len(self.type_inputed) == 0:
                CommonSent.no_void()
                continue
            break

    def input_option(self,option_num):
        """설정 번호 입력시 해당 입력값을 받아 return함.

        설정 번호
            0: 디렉토리/이름/타입
            1: 디렉토리
            2: 이름
            3: 이름/타입
        """
        if option_num == 0:
            self.__input_dir()
            self.__input_name()
            self.__input_type()
            return self.dir_inputed,self.name_inputed,self.type_inputed
        elif option_num == 1:
            self.__input_dir()
            return self.dir_inputed
        elif option_num == 2:
            self.__input_name()
            return self.name_inputed
        elif option_num == 3:
            self.__input_name()
            self.__input_type()
            return self.name_inputed,self.__input_type
