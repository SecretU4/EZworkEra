"""프로그램 내에서 사용되는 데이터를 결과물로 처리할 때 사용하는 모듈

Classes:
    InfoDict
    ERBMetaInfo
"""

class InfoDict:
    """코드 내에서 각 자료명을 파일명으로 분류해야 하는 경우 사용하는 자료형 클래스

    Functions:
        add_dict(dictname,data)
        make_dictvals_list()
    Variables:
        dict_main
            클래스 내 기록된 dict형 자료. {dictname:data} 형식
        db_ver
            기록 양식 확인용 클래스 버전
        dict_name_dictvals
            data가 dict형인 경우 함수 호출을 통해 사용 가능한 변수.\n
            {dictname:data.values()} 형식
    """
    def __init__(self):
        self.dict_main = {}
        self.dict_name_dictvals = {}

    db_ver = '1.1'

    def add_dict(self,dictname,dataname):
        """클래스 내 자료형에 새로운 정보 추가."""
        self.dict_main[dictname]=dataname

    def make_dictvals_list(self):
        """클래스 내 자료형 안의 data 중 dict형에 대해
        해당 dict의 value 값 list를 추출해 새로운 dict를 만듦.\n
        dict형이 아닌 data가 있을 시 작업 완료 후 메세지를 출력함.
        ex) {filename:[func1,func2,func3...]}
        """
        error_count = 0
        for name in list(self.dict_main):
            try:
                self.dict_name_dictvals[name]=list(self.dict_main[name].values())
            except AttributeError:
                error_count += 1
        if error_count != 0:
            print("작업 도중 dict형이 아닌 자료형이 확인되었습니다.")
        return self.dict_name_dictvals


class ERBMetaInfo:
    """ERB 파일 처리에 사용되는 자료형 클래스.
    작업시 각 line 처리시마다 level 변수와 count 변수의 처리가 필요함.

    Functions:
        add_line_list(str)
    Variables:
        db_ver
            기록 양식 확인용 클래스 버전
        linelist
            작업 완료시 결과 list. [[IF단계,CASE단계,CASE수,line]] 형식
        if_level
            IF문의 깊이 판단 변수
        case_level
            CASE/DATAFORM문의 깊이 판단 변수
        case_count
            CASE/DATAFORM문의 개수 판단 변수.
            CASE/DATAFORM 내 CASE/DATAFORM이 포함된 경우 정확하지 않을 수 있음.
    """
    def __init__(self):
        self.linelist = []
        self.if_level = 0
        self.case_level = 0
        self.case_count = 0

    db_ver = '1.1'

    def add_line_list(self,line):
        """linelist에 새로운 line 정보 추가"""
        self.linelist.append([self.if_level,self.case_level,self.case_count,line])
