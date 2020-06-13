"""내부 코드에서 공용으로 사용되는 기능 클래스 모듈.

Classes:
    CommonSent
    DataFilter
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
    def print_line(char='='):
        """구분선 생성"""
        print("".center(os.get_terminal_size().columns,char))

    @staticmethod
    def extract_finished():
        print("추출이 완료되었습니다.")
        time.sleep(1)

    @staticmethod
    def put_time(opt=0):
        """호출시의 시간 출력"""
        if opt == 1:
            target_time = time.strftime('%Y/%m/%d_%H:%M',time.localtime(time.time()))
        else: target_time = time.strftime('%Y/%m/%d %H:%M:%S',time.localtime(time.time()))
        return target_time


class DataFilter:
    """주어진 데이터를 처리하는 클래스

    Functions:
        dup_filter(list)
        erase_quote(data,quotechar)
    """
    def dup_filter(self, list_name):
        """list 내에서 중복되는 요소를 제거한 후 다시 list로 돌려줌."""
        dup_filtered = []
        set_filter = set()
        for data in list_name:
            if data not in set_filter:
                dup_filtered.append(data)
                set_filter.add(data)
        return dup_filtered

    def erase_quote(self,dataname,quotechar=';'):
        """입력받은 data(dict,list,str) 내 각 요소 중 quotechar 인자가 포함된 부분을 지움."""
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
        else:
            raise NotImplementedError


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

# 디버그용 코드
if __name__ == "__main__":
    pass
