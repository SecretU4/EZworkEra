"""내부 코드에서 공용으로 사용되는 기능 클래스 모듈.

Classes:
    CommonSent
    DataFilter
    MakeLog
"""
# 사용 라이브러리
import os
import pickle
import time
from customdb import InfoDict
from usefile import LoadFile
from System.interface import KoreanSupport
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
    def print_line():
        """구분선 생성"""
        print("".center(100,"="))

    @staticmethod
    def extract_finished():
        print("추출이 완료되었습니다.")
        time.sleep(1)

    @staticmethod
    def put_time():
        """호출시의 시간 출력"""
        return time.strftime('%Y/%m/%d %H:%M',time.localtime(time.time()))


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

    def erase_quote(self,dataname,quotechar):
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
                log_open.write('\n{} 실행됨\n'.format(CommonSent.put_time))
            else:
                log_open.write('\n{}\n{} 불러오기 성공.\n'.format(CommonSent.put_time,file_info))

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
            log_open.write('{} 오류 발생!'.format(error_code))
            if target != None:
                log_open.write('발생 위치: {}'.format(target))

    def write_loaded_log(self,filename):
        """작업 중 로드된 파일을 양식에 맞게 logfile에 기록함."""
        with self.addwrite() as log_open:
            log_open.write("파일명: {}".format(filename))

# 디버그용 코드
if __name__ == "__main__":
    pass

#TODO 설정 외부 파일화(xml나 config 등)
