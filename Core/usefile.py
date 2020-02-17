"""프로그램 내에서 사용되는 범용 클래스형 모듈 중 LoadFile과 연계된 모듈

Classes:
    LoadFile
    DirFilter
    FileFilter
    CustomInput
    MakeLog
    LogPreset
    MenuPreset
"""

import os
import time
import pickle
from util import CommonSent
from System.interface import Menu

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
        return open(self.NameDir, 'w', encoding=self.EncodeType)

    def readonly(self):
        """읽기 전용"""
        return open(self.NameDir, 'r', encoding=self.EncodeType, newline='')

    def addwrite(self):
        """있던 내용 뒤에 추가해 쓰기"""
        return open(self.NameDir, 'a', encoding=self.EncodeType)


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
            3: 상위 폴더명'만' 떼어냄
        example: origin = 'chara/char001/reimu.erb'\n
            opt0='reimu'
            opt1='chara/char001/reimu'
            opt2:'reimu.erb'
            opt3:'chara/char001/'
        """
        if self.option_num == 0:
            seprated_filename = os.path.splitext(os.path.basename(filename))[0]
        elif self.option_num == 1:
            seprated_filename = os.path.splitext(filename)[0]
        elif self.option_num == 2:
            seprated_filename = os.path.basename(filename)
        elif self.option_num == 3:
            seprated_filename = DirFilter(os.path.dirname(filename)).dir_slash()
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
        self.option_num = MenuPreset().yesno(0,"하위폴더까지 포함해 진행하시겠습니까?")
        encode_type = MenuPreset().encode()
        files = self.files_ext(target_dir,'.'+filetype)
        if self.option_num == 1: files = list(map(os.path.split,files))
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


class MakeLog(LoadFile):
    """작업 절차 중 log파일에 대한 클래스. 클래스 호출시 logfile명과 사용될 인코딩을 입력해야 한다.

    Functions:
        first_log(file_info)
        write_log(str)
        write_error_log(error_code,target)
        write_loaded_log(filename)
    Variables:
        NameDir
            log파일 명칭
    """
    def first_log(self,file_info=None):
        """작업 시작 절차를 logfile에 기록함. 입력받은 인자가 없으면 시작 시간만을 입력함."""
        with self.addwrite() as log_open:
            if file_info == None:
                log_open.write('[{}] Util Started\n'.format(CommonSent.put_time()))
            else:
                log_open.write('[{}] {} Loaded\n'.format(CommonSent.put_time(),file_info))

    def write_log(self,line='Defaultline'):
        """입력받은 str 타입 자료형을 logfile에 기록함.\n
        인자 미입력시 'DefaultLine'이 입력됨.
        """
        with self.addwrite() as log_open:
            log_open.write('{}'.format(line))

    def write_error_log(self,error_code,target=None):
        """입력받은 error 와 해당 위치(target)를 양식에 맞게 logfile에 기록함.\n
        target은 선택사항이고, 해당 경우 error_code만 입력됨.
        """
        with self.addwrite() as log_open:
            log_open.write('{} 오류 발생!\n'.format(error_code))
            if target != None:
                log_open.write('발생 위치: {}\n'.format(target))

    def write_loaded_log(self,filename):
        """작업 중 로드된 파일을 양식에 맞게 logfile에 기록함."""
        with self.addwrite() as log_open:
            log_open.write("{} loaded\n".format(filename))

    def end_log(self,workname=''):
        with self.addwrite() as log_open:
            log_open.write("[{}] {} done\n\n".format(
                CommonSent.put_time(),workname))


class LogPreset(MakeLog):
    def __init__(self,opt_arg=0):
        if type(opt_arg) == int:
            NameDir = 'debug.log'
            if opt_arg == 0: workclass = 'General'
            elif opt_arg == 1: workclass = 'CSVread'
            elif opt_arg == 2: workclass = 'ERBread'
            elif opt_arg == 3: workclass = 'ERBwrite'
            elif opt_arg == 4: workclass = 'Output'
            else: workclass = None
        elif type(opt_arg) == str:
            NameDir = opt_arg + '.log'
            workclass = opt_arg
        else: raise TypeError
        EncodeType = 'UTF-8'
        super().__init__(NameDir,EncodeType)
        self.first_log(workclass)
        self.workclass = workclass

    def if_decode_error(self):
        self.write_log("""유니코드 에러가 발생했다면:
오류코드 0xef는 UTF-8-sig, 다른 경우 cp932(일본어)나 cp949(한국어)로 시도하세요.\n\n
        """)

    def which_type_loaded(self,filetype):
        self.write_log("{} type file loaded\n".format(filetype))

    def sucessful_done(self):
        self.end_log(self.workclass)


class MenuPreset:
    """Menu 클래스를 사용한 자주 사용되는 프리셋 모음.

    Functions:
        encode()
        yesno(reverse,sentence)
        shall_save_data(data,datatype)
        load_saved_data(opt_no,[sentence])
    """
    def encode(self):
        """인코딩 선택시 해당 인코딩 str을 반환."""
        encode_dict={0:'UTF-8',1:'UTF-8 with BOM',2:'SHIFT-JIS',
                    3:'일본어 확장(cp932)',4:'EUC-KR',5:'한국어 확장(cp949)'}
        encode = Menu(encode_dict)
        encode.title("대상 파일의 인코딩을 선택하세요.")
        encode.run_menu()
        EncodeType = encode_dict[encode.selected_num]
        if EncodeType == 'UTF-8 with BOM':
            EncodeType = 'UTF-8-sig'
        elif EncodeType == '일본어 확장(cp932)':
            EncodeType = 'cp932'
        elif EncodeType == '한국어 확장(cp949)':
            EncodeType = 'cp949'
        return EncodeType

    def yesno(self,reverse,*sentences):
        """예/아니오 선택창. sentence로 선택창 앞에 문자열 출력 필요."""
        yesno_dict={0:'예',1:'아니오'}
        yesno = Menu(yesno_dict)
        yesno.title(*sentences)
        yesno.run_menu()
        if reverse:
            if yesno.selected_num == 0: return 1
            elif yesno.selected_num == 1: return 0
        else: return yesno.selected_num

    def shall_save_data(self,data,datatype=None):
        """추출된 데이터의 저장 메뉴. data가 저장될 데이터. 필요시 datatype 입력
        * 같은 이름의 sav파일 작성 불가.
        """
        menu_save = MenuPreset().yesno(0,"출력된 데이터를 외부 파일에 저장하시겠습니까?")
        DirFilter('sav').dir_exist()
        if menu_save == 0:
            while True:
                save_name = input("저장할 외부 파일의 이름을 입력해주세요.")
                try:
                    with open("sav\\{}_{}.sav".format(save_name,datatype), 'xb') as sav_file:
                        pickle.dump(data,sav_file,pickle.HIGHEST_PROTOCOL)
                        break
                except FileExistsError:
                    print("같은 이름의 파일이 존재합니다. 다시 시도해주세요.")

    def load_saved_data(self,opt_no=0,sentence=None):
        """저장해둔 데이터의 로드 메뉴.
        sentence:
            불러오기 화면에 추가로 표시할 문장.
        opt_no:
            0: 불러올지 말지 선택. 아니라면 None 반환.
            1: 무조건 불러옴.
        """
        yesno_sentence = "저장된 데이터 파일을 불러오시겠습니까?"
        please_choose_sent = "불러올 데이터 파일을 선택해주세요."
        if isinstance(sentence,str): yesno_sentence = sentence,yesno_sentence
        if opt_no == 0:
            load_switch = MenuPreset().yesno(0,*yesno_sentence)
            please_sent_lines = [please_choose_sent]
        elif opt_no == 1:
            load_switch = 0
            please_sent_lines = sentence,please_choose_sent
        if load_switch == 1:
            return None
        else:
            savfile_list = FileFilter().files_ext('sav','.sav')
            menu_sav_list = Menu(savfile_list)
            while True:
                menu_sav_list.title(*please_sent_lines)
                menu_sav_list.run_menu()
                self.selected_name = menu_sav_list.selected_menu
                if self.selected_name == "돌아가기": break
                with open(self.selected_name,'rb') as opened_sav:
                    target_data = pickle.load(opened_sav)
                    return target_data
