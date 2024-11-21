"""프로그램 내에서 사용되는 데이터를 결과물로 처리할 때 사용하는 모듈

Classes:
    InfoDict
    DFInfo
    ERBInfo
    FuncInfo
    SheetInfo
    SRSFormat
"""
import pandas


class InfoDict:
    """코드 내에서 각 자료명을 파일명으로 분류해야 하는 경우 사용하는 자료형 클래스

    Functions:
        add(dictname,data)
        make_dictvals_list()
        make_reverse()
    Variables:
        dict_main
            클래스 내 기록된 dict형 자료. {dictname:data} 형식
        db_ver
            기록 양식 확인용 클래스 버전
        dict_name_dictvals
            data가 dict형인 경우 함수 호출을 통해 사용 가능한 변수.\n
            {dictname:data.values()} 형식
    """

    def __init__(self, dbname=""):
        self.dict_main = {}
        self.dict_name_dictvals = {}
        self.dict_name_reverse = {}
        dbname_dict = {0:"CSVInfoDict" ,1:"ERBInfoDict", 2:"ERBMetaInfoDict"}
        if dbname_dict.get(dbname):
            dbname = dbname_dict[dbname]
        self.db_name = dbname
        self.db_ver = 1.31

    def add(self, dictname, dataname):
        """클래스 내 자료형에 새로운 정보 추가."""
        self.dict_main[dictname] = dataname

    def make_dictvals_list(self):
        """클래스 내 자료형 안의 data 중 dict형에 대해
        해당 dict의 value 값 list를 추출해 새로운 dict를 만듦.\n
        dict형이 아닌 data가 있을 시 작업 완료 후 메세지를 출력함.
        ex) {filename:[func1,func2,func3...]}
        """
        error_count = 0
        for name in list(self.dict_main):
            try:
                self.dict_name_dictvals[name] = list(self.dict_main[name].values())
            except AttributeError:
                error_count += 1
        if error_count != 0:
            print("작업 도중 dict형이 아닌 자료형이 확인되었습니다.")
        return self.dict_name_dictvals

    def make_reverse(self):
        """클래스 내 자료형 안의 data 중 dict형에 대해
        해당 dict의 key와 value 값을 뒤집음.\n
        dict형이 아닌 data가 있을 시 작업 완료 후 메세지를 출력함.
        ex) {filename:{A:B}} => {filename:{B:A}}
        """
        if self.dict_name_reverse:
            return self.dict_name_reverse
        error_count = 0

        for main_key in self.dict_main.keys():
            data = self.dict_main[main_key]
            try:
                reversed_data = {val: key for key, val in data.items()}
                self.dict_name_reverse[main_key] = reversed_data
            except AttributeError:
                error_count += 1

        if error_count:
            print("작업 도중 dict형이 아닌 자료형이 확인되었습니다.")
        return self.dict_name_reverse


class DFInfo:
    """pandas.DataFrame 활용 관련 데이터베이스 클래스. default index는 RangeIndex 고정을 상정함.

    Functions
        add_row(data)
        del_row(label, key)
        merge_df(dataframe)
        show_dict(label)
    Variables
        df
            DataFrame 본체
    """
    def __init__(self, labels=None, data=None):
        self.df = pandas.DataFrame(data=data, columns=labels)
    
    def add_row(self, *data):
        """맨 하단에 새로운 행 생성 함수"""
        self.df.loc[len(self.df)] = data

    def del_row(self, label, key):
        """선택한 label 중 key 에 해당하는 행 삭제 함수"""
        self.df = self.df.set_index(label).drop(key, axis=0)
        self.df.reset_index(inplace=True)

    def merge_df(self, dataframe, ing_index=True):
        """두 DataFrame의 병합 함수"""
        self.df = pandas.concat([self.df, dataframe], ignore_index=ing_index)
        return self.df

    def show_dict(self, label):
        """해당 label 값 기반의 dict 반환 함수"""
        return self.df.set_index(label).T.to_dict()


class ERBInfo(DFInfo):
    """ERB 파일의 Metainfolines 데이터베이스 클래스
    
    Functions
        make_indents()
        m_lines()
    Variables
        o_lines
            metainfolines 작성 이전 원본 lines
        db_ver
            기록 양식 확인용 클래스 버전
    """
    def __init__(self, lines):
        super().__init__(labels=["if_lv", "case_lv", "case_cnt", "line"])
        self.o_lines = lines
        self.db_ver = 1.0

    def _make_indent(self, metaline):
        if_lv, cases_lv, _, text = metaline
        f_line = "{}{}{}".format("\t" * if_lv, "\t" * cases_lv, text)
        if not text.endswith("\n"):
            f_line = f_line + "\n"
        return f_line

    def m_lines(self):
        """ERBMetaInfo.linelist 대응"""
        return self.df[["if_lv", "case_lv", "case_cnt", "line"]].values.tolist()

    def make_indents(self):
        """metaline을 들여쓰기된 lines로 만드는 함수. 처리시 df에 f_line 저장함. 이미 있다면 f_line 값 반환"""
        if 'f_line' in self.df.columns:
            return self.df["f_line"].to_list()
        f_lines:list[str] = []
        for m_line in self.m_lines():
            f_lines.append(self._make_indent(m_line))
        if f_lines == []:
            print("결과물이 없습니다.")
        else:
            self.df["f_line"] = f_lines
        return f_lines


class FuncInfo(DFInfo):
    """ERB의 정보를 함수별로 나누어 불러올 수 있는 자료형 클래스
    
    Functions
        add_row(funcname, data, [filename], [loc])
    Variables
        func_dict()
            함수별로 정리된 딕셔너리 자료형
        db_ver
            기록 양식 확인용 클래스 버전
    """

    def __init__(self):
        super().__init__(labels=["funcname","filename","loc","o_funcname","code"])
        self.df.astype({"loc":"int"})
        self.db_ver = 1.1

    def func_dict(self):
        return super().show_dict("funcname")

    def add_row(self, funcname, data, filename=None, loc=-1):
        """Function dict 추가 함수"""
        if len(self.df[self.df["funcname"] == funcname]):
            print("중복 함수: {} 발견, 추후 처리 요망".format(funcname))
        if loc == -1:
            loc = None
        super().add_row(funcname, filename, loc, funcname.split("(")[0], data)


class SheetInfo:
    """시트(표) 기반 자료형 클래스
    
    xlsx, sql 등으로 출력하고자 하는 자료에 사용
    * 자료의 추가, 조회만 지원함.
    """
    def __init__(self):
        # sheetdict = {sheetname: [dict(sheetinfo), data, data...]}
        # value의 각 요소가 하나의 행이라 보면 됨.
        # sheetinfo = {tags:(aaa,bbb,ccc...)}
        self.sheetdict = dict()
        self.db_ver = 1.0
    
    def add_sheet(self, sheetname="Main", datatags: list=None):
        """데이터 시트 추가 함수.
        sheetname : 시트의 이름, 기본값 Main
        datatags : 1열에 들어갈 데이터분류 태그 목록. 여기 없다면 기록되지 않음
        """
        sheetinfo = {"tags":datatags}
        dataset = [sheetinfo]
        if self.sheetdict.get(sheetname):
            sheetinfo, *dataset = self.sheetdict[sheetname]
            # datatags는 무조건 덮어쓰기로만 처리됨
            sheetinfo["tags"] = datatags
        
        dataset[0] = sheetinfo

        self.sheetdict.update({sheetname:dataset})

    def add_row(self, sheetname="Main", **kwargs):
        """행을 추가한 후 데이터를 입력함.

        기록 후 열이 남는 부분은 None으로 저장됨.
        """
        tags_exist = False
        target_sheet = self.sheetdict.get(sheetname)

        if not target_sheet:
            print("존재하지 않는 표 제목 %s" %sheetname)
            return None

        sheetinfo = target_sheet[0]
        target_data = dict()
    
        taginfo = sheetinfo["tags"]
        if isinstance(taginfo, list) or isinstance(taginfo, tuple):
            tags_exist = True
            for tag in taginfo:
                target_data[tag] = None

        for key, value in kwargs.items():
            if not tags_exist or key in taginfo: # taginfo에 존재하지 않는 태그는 통과함.
                target_data[key] = value
            
        target_sheet.append(target_data)
        self.sheetdict.update({sheetname:target_sheet})


class SRSFormat:
    """SRS 형식의 데이터 관리와 관련된 클래스"""
    def __init__(self, srsdict, dataname="ONLYSRS", srs_type=1):
        self.srsdict = srsdict
        self.dataname = dataname
        self.srs_type = srs_type
        self.db_ver = 1.0

    def _srstype_format(self):
        """srs_type 1:simplesrs 2:srs"""
        if self.srs_type == 1:
            fmtdata = {
                "pat":"$1#\n$2#\n\n",
                "head":True,
                "com":";comment\n\n"
            }
        elif self.srs_type == 2:
            fmtdata = {
                "pat":"[Search]\n$1#\n[Replace]\n$2#\n",               
                "head":False,
                "com":";comment\n"
            }
        else:
            raise NotImplementedError("지원하는 형식이 아닙니다")

        return fmtdata

    def set_head(self, h_opt):
        # TRIM:앞뒤공백 제거, SORT:긴 순서/알파벳 정렬, WORDWRAP:정확히 단어 단위일때만 치환
        head = ""
        if h_opt & 0b0001:
            head += "[-WORDWRAP-]"
        if h_opt & 0b0010:
            head += "[-TRIM-]"
        if h_opt & 0b0100:
            head += "[-REGEX-]"
        if h_opt & 0b1000:
            head += "[-SORT-]"
        if h_opt & 0b1100 >= 0b1100:
            raise TypeError("REGEX와 SORT 옵션은 동시 사용이 불가합니다")

        return head + '\n'

    def print_comment(self, sentence):
        return self._srstype_format()["com"].replace("comment", sentence)

    def print_srs(self, h_opt=0, title=False):
        """문자열 포함 list 형태로 srsdict 데이터를 변환"""
        result_lines = []
        fmtdata = self._srstype_format()

        if fmtdata["head"] and h_opt:
            result_lines.append(self.set_head(h_opt))

        if title:
            result_lines.append(self.print_comment("from: " +self.dataname))

        for key, value in self.srsdict.items():
            line = fmtdata["pat"].replace("$1#", key).replace("$2#", value)
            result_lines.append(line)

        return result_lines
