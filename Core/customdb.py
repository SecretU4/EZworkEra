"""프로그램 내에서 사용되는 데이터를 결과물로 처리할 때 사용하는 모듈"""

class InfoDict: # {파일명:{파일내 정보 딕셔너리형}}
    def __init__(self):
        self.dict_main = {}

    db_ver = '1.1'

    def add_dict(self,dictname,dataname):
        self.dict_main[dictname]=dataname

    def make_dictvals_list(self): # {파일명:[파일내 정보 딕셔너리.values()]}
        self.dict_name_dictvals = {}
        for name in list(self.dict_main):
            self.dict_name_dictvals[name]=list(self.dict_main[name].values())


class ERBMetaInfo: # [조건문단계,경우단계,경우수,해당 줄]
    def __init__(self):
        self.linelist = []
        self.if_level = 0
        self.case_level = 0
        self.case_count = 0

    db_ver = '1.1'

    def add_line_list(self,line):
        self.linelist.append([self.if_level,self.case_level,self.case_count,line])