# EZworkEra 공용 모듈
# 사용 라이브러리
import os
import pickle
import time
# 클래스 목록
## 사용자 화면 관련
class CommonSent: #관용구 클래스
    @staticmethod
    def not_ok():
        print("유효하지 않은 입력입니다.")
        time.sleep(0.5)

    @staticmethod
    def end_comment():
        print("이용해주셔서 감사합니다.")
        input("엔터를 누르면 종료됩니다.")

    @staticmethod
    def no_void():
        print("공란은 입력하실 수 없습니다.")
        time.sleep(0.5)

    @staticmethod
    def print_line():
        print("".center(100,"="))

    @staticmethod
    def extract_finished():
        print("추출이 완료되었습니다.")
        time.sleep(1)

    @staticmethod
    def put_time():
        return time.strftime('%Y/%m/%d %H:%M',time.localtime(time.time()))


class Menu: # 콘솔 메뉴 디스플레이
    def __init__(self,menu_dict):
        self.menu_dict = menu_dict

    def title(self,title_name):
        CommonSent.print_line()
        print(title_name.center(100," "))
        CommonSent.print_line()

    def __print_menu(self):
        for key in self.menu_dict:
            print("[{}]. {}".format(key,self.menu_dict[key]))
        CommonSent.print_line()
        self.selected_num = input("번호를 입력하세요. 클릭은 지원하지 않습니다. :")

    def run_menu(self):
        menu_numlist = tuple(self.menu_dict.keys())
        while True:
            self.__print_menu()
            try:
                self.selected_num = int(self.selected_num)
                if menu_numlist.count(self.selected_num) == True:
                    self.selected_menu = self.menu_dict[self.selected_num]
                    return self.selected_num
                elif self.selected_num == 99 or self.selected_num == 999:
                    print("디버그 기능 없습니다!")
                    time.sleep(0.5)
                else:
                    CommonSent.not_ok()
            except ValueError:
                CommonSent.not_ok()


class MenuPreset: # 자주 쓰는 메뉴 프리셋
    def encode(self):
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

    def yesno(self,sentence):
        yesno_dict={0:'예',1:'아니오'}
        yesno = Menu(yesno_dict)
        yesno.title(sentence)
        yesno.run_menu()
        return yesno.selected_num

    def shall_save_data(self,data,datatype=None):
        menu_save = MenuPreset().yesno("출력된 데이터를 외부 파일에 저장하시겠습니까?")
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

    def load_saved_data(self,option_num=0):
        if option_num == 0: # 불러올지 말지 정함
            menu_load = self.yesno("저장된 데이터 파일을 불러오시겠습니까?")
        elif option_num == 1: # 무조건 불러옴
            print("불러올 데이터 파일을 선택해주세요.")
            menu_load = 0
        if menu_load == 1:
            return None
        else:
            while True:
                sav_dir_list = DataFilter().files_ext('sav','.sav',1)
                sav_dir_list.append("돌아가기")
                menu_dict_sav_list = {}
                for filename in sav_dir_list:
                    menu_dict_sav_list[sav_dir_list.index(filename)]=filename
                menu_sav_list = Menu(menu_dict_sav_list)
                savfile_no = menu_sav_list.run_menu()
                self.savfile_name = menu_dict_sav_list[savfile_no]
                if self.savfile_name == "돌아가기": break
                with open(self.savfile_name,'rb') as opened_sav:
                    target_data = pickle.load(opened_sav)
                    return target_data
            return None


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


class InfoDict: # {파일명:{파일내 정보 딕셔너리형}}
    def __init__(self):
        self.dict_main = {}
        self.db_ver = '1.1'

    def add_dict(self,dictname,dataname):
        self.dict_main[dictname]=dataname

    def make_dictvals_list(self): # {파일명:[파일내 정보 딕셔너리.values()]}
        self.dict_name_dictvals = {}
        for name in list(self.dict_main):
            self.dict_name_dictvals[name]=list(self.dict_main[name].values())


class DataFilter:
    def dup_filter(self, list_name): #중복 감별 들어온 순서대로 저장
        dup_filtered = []
        set_filter = set()
        for data in list_name:
            if data not in set_filter:
                dup_filtered.append(data)
                set_filter.add(data)
        return dup_filtered

    def erase_quote(self,dataname,quotechar):
        if isinstance(dataname,dict) is True:
            dict_erased = {}
            for key in list(dataname.keys()):
                if quotechar in key: continue
                elif quotechar in dataname[key]: continue
                else:
                    dict_erased[key] = dataname[key]
            return dict_erased
        elif isinstance(dataname,list) is True:
            list_erased = []
            for data in dataname:
                if quotechar in data: continue
                else:
                    list_erased.append(data)
            return list_erased
        elif isinstance(dataname,str) is True:
            splited_data = dataname.split()
            try:
                if quotechar in splited_data[0]: return None
                else: return dataname
            except IndexError: return None

    def files_ext(self,dir_target,ext_target,option_num=0):
        ext_target = ext_target.upper()
        self.files = []
        if option_num == 0: # 하위 포함
            for (path, _, files) in os.walk(dir_target):
                for filename in files:
                    file_type = os.path.splitext(filename)[-1].upper()
                    if file_type == ext_target:
                        self.files.append('{0}\\{1}'.format(path,filename))
        elif option_num == 1: # 해당 디렉토리만
            for filename in os.listdir(dir_target):
                file_type = os.path.splitext(filename)[-1].upper()
                if file_type == ext_target:
                        self.files.append('{0}\\{1}'.format(dir_target,filename))
        return self.files

    def files_name(self,dir_target,name_target,option_num=0):
        name_target = name_target.upper()
        self.files = []
        if option_num == 0: # 하위 포함
            for (_, _, files) in os.walk(dir_target):
                for filename in files:
                    FoundName = os.path.split(filename)[-1].upper()
                    if name_target in FoundName:
                        self.files.append(FoundName)
        elif option_num == 1: # 해당 디렉토리만
            for filename in os.listdir(dir_target):
                FoundName = os.path.split(filename)[-1].upper()
                if name_target in FoundName:
                    self.files.append(FoundName)
        return self.files

    def sep_filename(self,filename,option_num=0): # 0: 오직 파일명 1: 확장자 제외 2: 상위폴더명 제외
        if option_num == 0:
            seprated_filename = os.path.basename(filename)
            seprated_filename = os.path.splitext(seprated_filename)[0]
        elif option_num == 1:
            seprated_filename = os.path.splitext(filename)[0]
        elif option_num == 2:
            seprated_filename = os.path.split(filename)[-1]
        return seprated_filename

    def search_filename_wordwrap(self,filenames,keyword_list):
        filename_dict = {}
        for filename in filenames:
            filename_dict[DataFilter().sep_filename(filename).upper().split()[0]] = filename
        for keyword in keyword_list:
            if keyword.upper() in list(filename_dict.keys()):
                target_name = filename_dict.get(keyword.upper())
                break
            else: target_name = None
        return target_name


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


class StatusNum: # 숫자 상태 처리 관련 클래스
    def __init__(self,target_data,target_type=None,logname=None,counted_num=0,error_num=0):
        self.total_num = len(target_data)
        self.counted_num = counted_num
        self.target_type = target_type
        self.error_num = error_num
        self.logname = logname
        if self.total_num < 10:
            self.when_num_show = [1,2]
        elif 10 <= self.total_num < 500:
            self.when_num_show = list(map(lambda x: x*int(
                round(self.total_num)/4), list(range(1,5))))
        else:
            self.when_num_show = list(map(lambda x: x*int(
                round(self.total_num)/10),list(range(1,11))))

    def how_much_there(self):
        print("{} 개의 {}{} 발견되었습니다.".format(self.total_num,self.target_type,
        KoreanSupport().what_next(self.target_type,'가')))

    def how_much_done(self):
        self.counted_num += 1
        if self.counted_num in self.when_num_show:
            print("{}/{} 완료".format(self.counted_num,self.total_num))
        elif self.counted_num == self.total_num:
            if self.error_num != 0:
                print("{} 개가 정상적으로 처리되지 않았습니다.".format(self.error_num))
                if self.logname != None:
                    print("{}를 확인해주세요.".format(self.logname))
            print("총 {} 개의 {} 중 {} 개가 처리 완료되었습니다.".format(self.total_num,
                self.target_type,self.total_num - self.error_num))


class KoreanSupport: # 한글 처리
    def is_hangul(self,word):
        self.last_letter = list(word)[-1]
        if ord(self.last_letter) < 0xac00 or ord(self.last_letter) > 0xD7A3:
            return False
        return True

    def have_jongseong(self,word):
        if self.is_hangul(word) == False: return None
        self.jongseong_code = (ord(self.last_letter) - 0xac00)%28
        if self.jongseong_code == 0:
            return 0 # 종성 없음
        else: return 1 # 종성 있음

    def what_next(self,word,josa):
        is_jongseong = self.have_jongseong(word)
        josa_list = [['이','가'],['을','를'],['은','는'],['와','과']]
        if is_jongseong == None:
            return '한글아님'
        josa_type = [bulk for bulk in josa_list if josa in bulk]
        if is_jongseong == 0:
            for bulk in josa_type:
                return bulk[1]
        elif is_jongseong == 1:
            for bulk in josa_type:
                return bulk[0]


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


class MakeLog(LoadFile):
    def first_log(self,file_info=None):
        with self.addwrite() as log_open:
            if file_info == None:
                log_open.write('\n{} 실행됨\n'.format(CommonSent.put_time))
            else:
                log_open.write('\n{}\n{} 불러오기 성공.\n'.format(CommonSent.put_time,file_info))

    def write_log(self,line='defaultline'):
        with self.addwrite() as log_open:
            log_open.write('{}'.format(line))

    def write_error_log(self,error_code,line=None):
        with self.addwrite() as log_open:
            log_open.write('{} 오류 발생!'.format(error_code))
            if line != None:
                log_open.write('발생 위치: {}'.format(line))

# 디버그용 코드
if __name__ == "__main__":
    debug_menu = Menu({0:"테스트",1:"스크린"})
    debug_menu.title("디버그 테스트 메뉴")
    debug_menu.run_menu()
    print(debug_menu.selected_num)
    print(MenuPreset().encode())

#TODO GUI 인터페이스 지원 - 구상 번역기만이라도.
#TODO 설정 외부 파일화(xml나 config 등)
