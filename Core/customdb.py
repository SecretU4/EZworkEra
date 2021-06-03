"""프로그램 내에서 사용되는 데이터를 결과물로 처리할 때 사용하는 모듈

Classes:
    InfoDict
    ERBMetaInfo
    FuncInfo
    SheetInfo
    SRSFormat
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

    def __init__(self, dbname=""):
        self.dict_main = {}
        self.dict_name_dictvals = {}
        self.dict_name_reverse = {}
        if type(dbname) == int:
            if dbname == 0:
                dbname = "CSVInfoDict"
            elif dbname == 1:
                dbname = "ERBInfoDict"
            elif dbname == 2:
                dbname = "ERBMetaInfoDict"
        self.db_name = dbname
        self.db_ver = 1.3

    def add_dict(self, dictname, dataname):
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
        blocklist
            작업 완료시 코드블럭 list. [[블럭 계층,코드 타입,[blocklines]]] 형식
        if_level
            IF문의 깊이 판단 변수
        case_level
            CASE/DATAFORM문의 깊이 판단 변수
        case_count
            CASE/DATAFORM문의 개수 판단 변수.
            CASE/DATAFORM 내 CASE/DATAFORM이 포함된 경우 정확하지 않을 수 있음.
    """

    def __init__(self, mod_no=0):
        # mod_no bit 1= 0:전부 1: 기능관련만 bit 2= 0:전부 1:추가주석 제외
        self.linelist = []
        self.blocklist = []
        self.blocklines = []
        self.block_check = 0
        self.__reset_count()
        self.case_check = {}
        self.mod_no = mod_no
        self.db_ver = 1.3

    def __reset_count(self):
        self.if_level = 0
        self.case_level = 0
        self.on_datalist = 0

    def case_count(self, stat=0, case_level=0):
        """분기문 개수 판별 함수
        stat 1: count 1 추가, -1: 해당 case_level의 count 초기화
        """
        if not case_level:
            case_level = self.case_level

        if self.case_check.get(case_level):
            count = self.case_check[case_level]
        else:
            count = 0
        
        if stat == -1:
            count = self.case_check.pop(case_level)
        elif not stat:
            pass
        else:
            count = max(count + stat, 0)
            self.case_check[case_level] = count
        return count

    def add_line_list(self, line):
        """linelist에 새로운 line 정보 추가"""
        self.linelist.append([self.if_level, self.case_level, self.case_count(), line])

    def add_linelist_embeded(self, line):  # TODO 코드 블럭 인식 기능
        """line 데이터 처리 함수

        0 리턴시 정상 작동 증명
        None 발생시 상정되지 않은 상황 발생
        """
        line = line.strip()
        back_count = 0
        if self.linelist:
            bef_status = self.linelist[-1]  # 작업 직전의 [if_level,case_level,case_count,line]
            while not bef_status[-1]:  # line 이 공란일 때
                back_count += 1
                bef_status = self.linelist[-(back_count + 1)]  # line이 있었던 곳까지 돌아감
        else:
            bef_status = 0
        while True:
            if "PRINT" in line:
                if "PRINTDATA" in line:
                    self.add_line_list(line)
                    self.case_level += 1
                else:
                    if self.mod_no & 0b1:
                        break
                    self.add_line_list(line)
                break
            elif "IF" in line:
                if "ENDIF" in line:
                    self.if_level -= 1
                    self.add_line_list(line)
                elif line.startswith("IF"):
                    self.add_line_list(line)
                    self.if_level += 1
                elif "ELSEIF" in line:
                    self.if_level -= 1
                    self.add_line_list(line)
                    self.if_level += 1
                elif "SIF" in line:
                    self.add_line_list(line)
                else:
                    return None
                break
            elif self.case_level != 0:  # 케이스 내부 돌 때
                if "CASE" in line:
                    if "SELECTCASE" in line:
                        self.add_line_list(line)
                        self.case_level += 1
                    elif line.startswith("CASE"):
                        if self.case_count(case_level=self.case_level - 1):
                            self.case_level -= 1
                        self.case_count(1)
                        if self.mod_no & 0b1:
                            return 1
                        self.add_line_list(line)
                        self.case_level += 1
                    else:
                        return None
                    return 0
                elif "DATA" in line:
                    if "DATAFORM" in line:
                        if not self.on_datalist:
                            self.case_count(1)
                        if self.mod_no & 0b1:
                            break
                        self.add_line_list(line)
                    elif "DATALIST" in line:
                        self.case_count(1)
                        self.on_datalist = 1
                        if self.mod_no & 0b1:
                            self.case_level += 1
                            break
                        self.add_line_list(line)
                        self.case_level += 1
                    elif "PRINTDATA" in line:
                        self.add_line_list(line)
                        self.case_level += 1
                        print("분기문 안에 분기문이 있습니다.")
                    elif "ENDDATA" in line:
                        cas_count = self.case_count(-1)
                        self.case_level -= 1
                        if not self.mod_no & 0b10:
                            line = line + " ;{}개의 케이스 존재".format(cas_count)
                        self.add_line_list(line)
                    else:
                        return None
                    break
                elif "END" in line:
                    if "ENDSELECT" in line:
                        self.case_level -= 1
                        cas_count = self.case_count(-1)
                        if not self.mod_no & 0b10:
                            line = line + " ;{}개의 케이스 존재".format(cas_count)
                        self.case_level -= 1
                        self.add_line_list(line)
                    elif "ENDLIST" in line:
                        self.case_level -= 1
                        self.on_datalist = 0
                        if self.mod_no & 0b1:
                            break
                        self.add_line_list(line)
                    else:
                        return None
                    break
                else:
                    pass
            if "SELECTCASE" in line:
                self.add_line_list(line)
                self.case_level += 1
            elif line.startswith("ELSE"):
                self.if_level -= 1
                self.add_line_list(line)
                self.if_level += 1
            elif line.startswith("RETURN"):
                self.add_line_list(line)
            elif line.startswith("GOTO"):
                self.add_line_list(line)
            elif line.startswith("#"):
                self.add_line_list(line)
            elif line.startswith("LOCAL"):
                self.add_line_list(line)
            elif line.startswith("$"):
                self.add_line_list(line)
            elif line.startswith("@"):
                self.__reset_count()
                self.add_line_list(line)
            else:
                if self.mod_no & 0b1:
                    break
                self.add_line_list(line)
            break
        if bef_status:
            if self.if_level != bef_status[0]:
                if self.if_level > bef_status[0]:  # if 블럭 스타트
                    pass
                elif self.if_level < bef_status[0]:  # if 블럭 종료
                    pass
            elif self.case_level != bef_status[1]:
                if self.case_level > bef_status[1]:  # case 블럭 스타트
                    pass
                elif self.case_level < bef_status[1]:  # case 블럭 종료
                    pass
        return 0

    def printable_lines(self):
        """metainfo가 없는 순수 리스트 저장"""
        lines = []
        for metadata in self.linelist:
            lines.append(metadata[-1])
        return lines


class FuncInfo:
    """ERB의 정보를 함수별로 나누어 불러올 수 있는 자료형 클래스
    
    Functions
        add_dict(funcname, data, [filename])
    Variables
        func_dict
            함수별로 정리된 딕셔너리 자료형
        file_func_dict
            파일/함수별로 정리된 딕셔너리 자료형
        db_ver
            기록 양식 확인용 클래스 버전
    """

    def __init__(self):
        self.db_ver = 1.0
        self.file_func_dict = dict()
        self.func_dict = dict()

    def add_dict(self, funcname, data, filename=None):
        self.func_dict[funcname] = data

        if filename:
            data_already = self.file_func_dict.get(filename)
            if type(data_already) == type(data):
                if isinstance(data_already, dict):
                    data_already.update(data)
                elif isinstance(data_already, list):
                    data_already.extend(data)
                else:
                    raise TypeError(type(data))
            else:
                data_already = data
            self.file_func_dict[filename] = data_already


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
    
    def add_sheet(self, sheetname="Main", datatags=None):
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

    def srstype_format(self):
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
        if (h_opt & 0b1000) and (h_opt & 0b0100):
            raise TypeError("REGEX와 SORT 옵션은 동시 사용이 불가합니다")

        return head + '\n'

    def print_comment(self, sentence):
        return self.srstype_format()["com"].replace("comment", sentence)

    def print_srs(self, h_opt=0, title=False):
        """문자열 포함 list 형태로 srsdict 데이터를 변환"""
        result_lines = []
        fmtdata = self.srstype_format()

        if fmtdata["head"] and h_opt:
            result_lines.append(self.set_head(h_opt))

        if title:
            result_lines.append(self.print_comment("from: " +self.dataname))

        for key, value in self.srsdict.items():
            line = fmtdata["pat"].replace("$1#", key).replace("$2#", value)
            result_lines.append(line)

        return result_lines
