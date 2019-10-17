# EZworkEra 메인 모듈
# 사용 라이브러리
import os
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


class Menu: # 콘솔 메뉴 디스플레이
    def __init__(self,menu_dict):
        self.menu_dict = menu_dict

    def title(self,title_name):
        CommonSent.print_line()
        print(title_name.center(100," "))
        CommonSent.print_line()

    def _print_menu(self):
        for key in self.menu_dict:
            print("[{}]. {}".format(key,self.menu_dict[key]))
        CommonSent.print_line()
        self.selected_num = input("번호를 입력하세요. 클릭은 지원하지 않습니다. :")

    def run_menu(self):
        menu_numlist = tuple(self.menu_dict.keys())
        while True:
            self._print_menu()
            try:
                self.selected_num = int(self.selected_num)
                if menu_numlist.count(self.selected_num) == True:
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
        self.dir_inputed = DataFilter().dir_slash(self.dir_inputed)

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


class DictInfo: # 파일 이름별 사전 저장
    dict_info = {}
    def add_dict(self,dictname,dict):
        self.dict_info[dictname]=dict

    def show_dict_list(self):
        return self.dict_info.keys


class DataFilter:
    def dir_slash(self, dir):
        dir_slashed = list(dir)
        if list(dir) == []: pass
        elif dir_slashed.pop() != "/": dir = dir + "/"
        return dir

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
                        self.files.append('{0}/{1}'.format(path,filename))
        elif option_num == 1: # 해당 디렉토리만
            for filename in os.listdir(dir_target):
                file_type = os.path.splitext(filename)[-1].upper()
                if file_type == ext_target:
                        self.files.append('{0}/{1}'.format(path,filename))
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

    def sep_filename(self,filename):
        splited_filename = os.path.basename(filename)
        filename_only = os.path.splitext(splited_filename)[0]
        return filename_only


class LoadFile: # 파일 불러오기 상용구
    def __init__(self, NameDir, EncodeType='UTF-8'):
        self.NameDir = NameDir
        self.EncodType = EncodeType

    def onlyopen(self): return open(self.NameDir)

    def readwrite(self):
        return open(self.NameDir, 'w', encoding=self.EncodType, newline='')

    def readonly(self):
        return open(self.NameDir, 'r', encoding=self.EncodType, newline='')

    def addwrite(self):
        return open(self.NameDir, 'a', encoding=self.EncodType, newline='')

# 디버그용 코드
if __name__ == "__main__":
    debug_menu = Menu({0:"테스트",1:"스크린"})
    debug_menu.title("디버그 테스트 메뉴")
    debug_menu.run_menu()
    print(debug_menu.selected_num)
    print(MenuPreset().encode())
