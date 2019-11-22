"""프로그램 내에서 사용자에게 보여주는 인터페이스 관련 모듈.

Classes:
    Menu
    MenuPreset
    KoreanSupport
    StatusNum
"""

import pickle
import time
import re
from Core.util import CommonSent
from Core.usefile import DirFilter, FileFilter
class Menu:
    """입력받은 자료형({int:str} 또는 [str]) 기반 메뉴창 표출 및 입력값 받음.
    * dict의 경우 '돌아가기'가 생성되지 않음.

    Functions:
        title(str)
        run_menu()

    Variables:
        selected_num
        selected_menu
    """
    def __init__(self,menu_data):
        if isinstance(menu_data,dict):
            for key in list(menu_data.keys()):
                if re.compile('[^0-9]').match(key):
                    raise TypeError
            self.menu_dict = menu_data
        elif isinstance(menu_data,list):
            menu_data.append("돌아가기")
            self.menu_dict = {}
            for keyname in menu_data:
                self.menu_dict[menu_data.index(keyname)]=keyname
        else: raise TypeError

    def __print_menu(self):
        for key in self.menu_dict:
            print("[{}]. {}".format(key,self.menu_dict[key]))
        CommonSent.print_line()
        self.selected_num = input("번호를 입력하세요. 클릭은 지원하지 않습니다. :")

    def title(self,title_name):
        """메뉴 제목용 함수. 메뉴 내 문장 출력에도 사용 가능"""
        CommonSent.print_line()
        print(title_name.center(100," "))
        CommonSent.print_line()

    def run_menu(self):
        """입력 정보를 int로 변환 후 해당하는 선택지가 있을 때 해당 숫자 반환함. 다른 경우 루프."""
        menu_numlist = tuple(self.menu_dict.keys())
        while True:
            self.__print_menu()
            try:
                self.selected_num = int(self.selected_num)
                if menu_numlist.count(self.selected_num) == True:
                    self.selected_menu = self.menu_dict[self.selected_num]
                    return self.selected_num
                # EasterEgg
                elif self.selected_num == 99 or self.selected_num == 999:
                    print("디버그 기능 없습니다!")
                    time.sleep(0.5)
                else:
                    CommonSent.not_ok()
            except ValueError:
                CommonSent.not_ok()


class MenuPreset:
    """Menu 클래스를 사용한 자주 사용되는 프리셋 모음.

    Functions:
        encode()
        yesno(sentence)
        shall_save_data(data,datatype)
        load_saved_data(opt_no)
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

    def yesno(self,sentence):
        """예/아니오 선택창. sentence로 선택창 앞에 문자열 출력 필요."""
        yesno_dict={0:'예',1:'아니오'}
        yesno = Menu(yesno_dict)
        yesno.title(sentence)
        yesno.run_menu()
        return yesno.selected_num

    def shall_save_data(self,data,datatype=None):
        """추출된 데이터의 저장 메뉴. data가 저장될 데이터. 필요시 datatype 입력
        * 같은 이름의 sav파일 작성 불가.
        """
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

    def load_saved_data(self,opt_no=0):
        """저장해둔 데이터의 로드 메뉴.

        opt_no:
            0: 불러올지 말지 선택. 아니라면 None 반환.
            1: 무조건 불러옴.
        """
        if opt_no == 0:
            load_switch = MenuPreset().yesno("저장된 데이터 파일을 불러오시겠습니까?")
        elif opt_no == 1:
            print("불러올 데이터 파일을 선택해주세요.")
            load_switch = 0
        if load_switch == 1:
            return None
        else:
            savfile_list = FileFilter().files_ext('sav','.sav',1)
            menu_sav_list = Menu(savfile_list)
            while True:
                menu_sav_list.run_menu()
                self.selected_name = menu_sav_list.selected_menu
                if self.selected_name == "돌아가기": break
                with open(self.selected_name,'rb') as opened_sav:
                    target_data = pickle.load(opened_sav)
                    return target_data
            return None


class KoreanSupport:
    """한글 여부 및 조사 처리 클래스"""
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


class StatusNum:
    """숫자 상태 처리 관련 클래스.

    Required args:
        target_data - 작업 대상물(반복 가능한것)

    Optional args:
        target_type
            작업 대상물 타입
        logname
            해당 작업에서의 로그파일명

    Functions:
        how_much_there()
        how_much_done()

    Variables:
        counted_num
            지금까지 작업한 수
        error_num
            작업 도중 발생한 에러의 수. 작업 중 외부 입력절차 필요.
    """
    def __init__(self,target_data,target_type='jobs',logname=None,counted_num=0,error_num=0):
        """인자 설명(모듈에 쓴 것 제외):

            when_num_show
                how_much_done()에서 몇번째 파일이 완료되었을 때 문장을 출력할지를 지정.
        """
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
        """작업 시작시 작업물 개수 출력 함수."""
        print("{} 개의 {}{} 발견되었습니다.".format(self.total_num,self.target_type,
        KoreanSupport().what_next(self.target_type,'가')))

    def how_much_done(self):
        """진행도 확인 함수. 반복문 블럭 안 맨 뒤에 넣는다.
        * logname 작성시 오류 발생한 경우 해당 문자열 출력함.
        """
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


#TODO GUI 인터페이스 지원 - 구상 번역기만이라도.
