"""내부 코드에서 공용으로 사용되는 기능 클래스 모듈.

Classes:
    CommonSent
    DataFilter
    DupItemCheck
    KoreanSupport
"""
# 사용 라이브러리
import os
import pickle
import time

# 클래스 목록
class CommonSent:
    """자주 사용되는 관용구 묶음 클래스. 모든 함수는 staticmethod로, 클래스의 self를 선언하지 않는다.

    Functions:
        not_ok()
        end_comment()
        no_void()
        print_line()
        extract_finished()
        put_time()
    """

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
    def print_line(char="="):
        """구분선 생성"""
        print("".center(os.get_terminal_size().columns, char))

    @staticmethod
    def extract_finished():
        print("추출이 완료되었습니다.")
        time.sleep(1)

    @staticmethod
    def put_time(opt=0):
        """호출시의 시간 출력"""
        if opt == 1:
            target_time = time.strftime("%Y-%m-%d_%H:%M", time.localtime(time.time()))
        else:
            target_time = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(time.time()))
        return target_time


class DataFilter:
    """주어진 데이터를 처리하는 클래스

    Functions:
        dup_filter(data)
        erase_quote(data,quotechar)
        strip_filter(data)
    """

    def dup_filter(self, data: list):
        """list 내에서 중복되는 요소를 제거한 후 다시 list로 돌려줌."""
        dup_filtered = []
        set_filter = set()
        for arg in data:
            if arg not in set_filter:
                dup_filtered.append(arg)
                set_filter.add(arg)
        return dup_filtered

    def erase_quote(self, data: str or dict or list, quotechar=";", opt: int=0):
        """입력받은 data(str, dict, list) 내 각 요소 중 quotechar 인자가 포함된 부분을 지움.
        
        opt 0: 해당 요소 삭제 후 반환, 1:해당 요소 내 quotechar 뒤를 제거한 data 반환
        """
        if isinstance(data, str):
            if quotechar not in data:
                return data
            elif opt == 1: # quotechar가 data 안에 있음
                return data.split(quotechar)[0]
        elif isinstance(data, dict):
            dict_erased = {}
            for key, val in data.items():
                if quotechar not in key and quotechar not in val:
                    dict_erased[key] = val
                elif opt == 1 and quotechar in val: # key에 quotechar가 있는 경우 제외
                    dict_erased[key] = self.erase_quote(val, quotechar, 1)
            return dict_erased
        elif isinstance(data, list):
            list_erased = []
            for arg in data:
                if quotechar not in arg:
                    list_erased.append(arg)
                elif opt == 1:
                    arg = self.erase_quote(arg, quotechar, 1)
                    list_erased.append(arg)
            return list_erased
        else:
            raise TypeError
        
    def strip_filter(self, data: list):
        """받은 list자료 내 요소에 strip처리 후 반환"""
        result_list = []
        error_flag = 0
        for arg in data:
            if not isinstance(arg, str):
                result_list.append(arg)
                error_flag |= 0b0001
                continue

            result_list.append(arg.strip())

        if error_flag:
            print("오류 코드: %d" % error_flag)
        
        return result_list
            

class DupItemCheck:
    """dict 자료형 내 중복요소 확인.

    1:key 2:value 3:key,value 둘다 있음

    사용시 check 로 체크 후 after로 검사요소 추가.
    dup_dict 여부로 중복 여부 확인
    """
    def __init__(self, main_dict={}, dup_dict={}):
        self.main_dict = main_dict
        self.dup_dict = dup_dict
    
    def check(self, key, value):
        for arg in (key, value):
            if key == value:
                return -1
    
            if self.main_dict.get(arg):
                dup_val = self.dup_dict.get(arg)
                if not dup_val:
                    self.dup_dict[arg] = self.main_dict[arg]
                elif dup_val == 1 and arg == key:
                    pass
                elif dup_val == 2 and arg == value:
                    pass
                else:
                    self.dup_dict[arg] = 3
                return self.dup_dict[arg]

        return 0

    def after(self, key, value):
        self.main_dict[key] = 1
        self.main_dict[value] = 2

    def bulkcheck(self, srs_data):
        self.__init__()
        for key, value in srs_data.items():
            self.check(key, value)
            self.after(key, value)

        return self.dup_dict

    def tot_dup(self):
        return self.main_dict, self.dup_dict


class KoreanSupport:
    """한글 여부 및 조사 처리 클래스"""

    def is_hangul(self, word):
        self.last_letter = list(word)[-1]
        if ord(self.last_letter) < 0xAC00 or ord(self.last_letter) > 0xD7A3:
            return False
        return True

    def have_jongseong(self, word):
        if self.is_hangul(word) == False:
            return None
        self.jongseong_code = (ord(self.last_letter) - 0xAC00) % 28
        if self.jongseong_code == 0:
            return 0  # 종성 없음
        else:
            return 1  # 종성 있음

    def what_next(self, word, josa):
        is_jongseong = self.have_jongseong(word)
        josa_list = [["이", "가"], ["을", "를"], ["은", "는"], ["와", "과"]]
        if is_jongseong == None:
            return "한글아님"
        josa_type = [bulk for bulk in josa_list if josa in bulk]
        if is_jongseong == 0:
            for bulk in josa_type:
                return bulk[1]
        elif is_jongseong == 1:
            for bulk in josa_type:
                return bulk[0]


# 디버그용 코드
if __name__ == "__main__":
    pass
