# EZworkEra 공용 모듈
# 사용 라이브러리
import os
import pickle
import time
from customdb import InfoDict
from usefile import LoadFile
from System.interface import KoreanSupport
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


class MakeLog(LoadFile):
    def first_log(self,file_info=None):
        with self.addwrite() as log_open:
            if file_info == None:
                log_open.write('\n{} 실행됨\n'.format(CommonSent.put_time))
            else:
                log_open.write('\n{}\n{} 불러오기 성공.\n'.format(CommonSent.put_time,file_info))

    def write_log(self,line='Defaultline'):
        with self.addwrite() as log_open:
            log_open.write('{}'.format(line))

    def write_error_log(self,error_code,target=None):
        with self.addwrite() as log_open:
            log_open.write('{} 오류 발생!'.format(error_code))
            if target != None:
                log_open.write('발생 위치: {}'.format(target))

    def write_loaded_log(self,filename):
        with self.addwrite() as log_open:
            log_open.write("파일명: {}".format(filename))

# 디버그용 코드
if __name__ == "__main__":
    pass

#TODO 설정 외부 파일화(xml나 config 등)
