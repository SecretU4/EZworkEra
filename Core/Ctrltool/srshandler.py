# simplesrs, srs 관련 처리 모듈

from customdb import InfoDict, SheetInfo, SRSFormat
from usefile import CustomInput, FileFilter, LoadFile, MenuPreset
from util import DataFilter, DupItemCheck


class SRSFile(LoadFile):
    """이미 존재하는 srs계열 파일의 처리 관련 클래스"""
    def __init__(self, srsname, encoding='UTF-8'):
        super().__init__(srsname, encoding)

        with self.readonly() as loaded:
            self.bulkiiles = loaded.readlines()
            self.strbulk = loaded.read()
        self.srs_bulk = DataFilter().strip_filter(self.bulkiiles)

    def check_srstype(self):
        """return 0: non-srs 1: simplesr 2: srs """
        sample = dict()
        for count, line in enumerate(self.srs_bulk):
            if line.startswith(("[-TRIM-]","[-WORDWRAP-]","[-SORT-]","[-REGEX-]")):
                return 1
            elif line in ("[Search]","[Replace]"):
                return 2
            if not line and sample.get(count - 1):
                return 1
            elif line:
                sample[count] = line
    
        return 0

    def make_dict(self, total_data={}, dup_data={}, head_flag=True, srs_type=None):
        if srs_type == None:
            srs_type = self.check_srstype()

        if srs_type == 0: # srs 관련 양식이 아님
            raise TypeError
        elif srs_type == 2: # srs는 HEAD 미지원
            context_flag = False
            head_flag = False

        result_dict = dict()
        dup_check = DupItemCheck(total_data, dup_data)
        orig = ''

        for count, line in enumerate(self.srs_bulk):
            if count == 0 and head_flag:
                continue
            
            if srs_type == 1: # simplesrs
                if line == '':
                    orig = ''
                elif orig == '':
                    orig = line
                else:
                    dup_check.check(orig, line)
                    result_dict[orig] = line
                    dup_check.after(orig, line)
                    orig = ''

            elif srs_type == 2: # srs
                upcount = count + 1
                # 범위 초과
                if len(self.srs_bulk) < upcount:
                    break
                # [Search] 내용 또는 [Replace] 내용
                elif context_flag:
                    context_flag = False
                    continue
                contextline = self.srs_bulk[upcount]
                if line.startswith("[Replace]"):
                    if not orig:
                        raise IndexError("잘못된 srs 양식 @ %d" % upcount)
                    dup_check.check(orig, contextline)
                    result_dict[orig] = contextline
                    dup_check.after(orig, contextline)
                    orig = ''
                    context_flag = True
                elif line.startswith("[Search]"):
                    orig = contextline
                    context_flag = True
            else:
                raise NotImplementedError
        
        return result_dict, dup_check


class SRSConvert:
    """srs 내용을 다른 형태로 변환하는 클래스"""
    def make_srs_to_sheet(self, srs_dict, sheetname="srs-sheet", srs_type=None, total_data={}, dup_data={}):
        result_sheet = SheetInfo()
        result_sheet.add_sheet(sheetname, ['orig_name', 'trans_name'])
        dup_check = DupItemCheck(total_data, dup_data)
        dup_check.bulkcheck(srs_dict)

        for key, value in srs_dict.items():
            result_sheet.add_row(sheetname, orig_name=key, trans_name=value)

        if dup_check.dup_dict:
            print("중복되는 요소들이 발견되었습니다.")

        return result_sheet, dup_check


class SRSEditor:
    """srs 내용을 편집하는 클래스"""
    def merge(self, *files, encoding='UTF-8'):
        result_dict = dict()
        total_data = {}
        dup_data = {}
        for filename in files:
            srs_dict, dup_check = SRSFile(filename, encoding).make_dict(total_data, dup_data)
            result_dict.update(srs_dict)
            total_data.update(dup_check.main_dict)
            dup_data.update(dup_check.dup_dict)

            if dup_check.dup_dict:
                print("%s 내부에서 중복되는 요소들이 발견되었습니다." % filename)

        return result_dict
    
    def advanced_filter(self, srs_dict, opt_no=0):
        if not srs_dict:
            print("작업할 내용물이 없습니다")
            return False

        result_dict = {}
        filtered = [ [],[] ]
        for key, value in srs_dict.items():
            if opt_no: # 모드 설정이 하나 이상 있을때
                if opt_no & 0b1 and key == value: # 미번역 단어 제외
                    filtered[0].append(key)
                    continue
                if opt_no & 0b10 and len(key) < 2: # 짧은 단어 필터링
                    filtered[1].append(key)
                    continue
                if opt_no & 0b100: # CSV 표적화 - CSV 기반 srs의 ERB 처리용
                    key = ":" + key
                    value = ":" + value
                elif opt_no & 0b1000: # CSV 표적화 - Chara CSV 내 인명(NAME, CALLNAME) 처리용
                    result_dict["名前,%s"% key] = "名前,%s"% value
                    key = "呼び名," + key
                    value = "呼び名," + value

            result_dict[key] = value

        return result_dict, filtered


class SRSMaker:
    """주어진 복수의 자료를 dict형으로 변환해 srs화하기 쉽게 해줌"""
    def __init__(self, data:tuple):
        if len(data) != 2:
            raise IndexError("데이터 갯수가 올바르지 않습니다")
        self.data = data

    def _check_datatype(self, data_1, data_2, text: str ="") -> list(tuple):
        result: list(tuple) = []
        have_null = {}
        if type(data_1) == type(data_2):
            if isinstance(data_1, InfoDict):
                a_dict:dict = data_1.dict_main
                b_dict:dict = data_2.dict_main
                sep_name = FileFilter(0).sep_filename
                datadict_a = {sep_name(key): val for key, val in a_dict.items()}
                datadict_b = {sep_name(key): val for key, val in b_dict.items()}
                result, have_null = self._check_datatype(datadict_a, datadict_b, "InfoDict 내부 ")
            elif isinstance(data_1, dict):
                keys_1 = list(data_1.keys())
                keys_2 = list(data_2.keys())
                total_keys = DataFilter().dup_filter(keys_1 + keys_2)
                for t_key in total_keys:
                    if t_key not in keys_1:
                        have_null[t_key] = 1
                    elif t_key not in keys_2:
                        have_null[t_key] = 2
                    else:
                        result.append( (data_1[t_key], data_2[t_key]) )
            elif isinstance(data_1, (list,tuple)):
                if len(data_1) != len(data_2):
                    print("두 자료의 길이가 일치하지 않습니다. 일부 자료가 누락되었습니다.")
                f_strip = DataFilter().strip_filter
                result = list(zip(f_strip(data_1), f_strip(data_2)))
            else:
                raise NotImplementedError("지원하지 않는 자료형: " + type(data_1))
        else:
            raise TypeError("%s두 데이터의 자료형이 같지 않습니다." % text)

        return result, have_null

    def make_srsdict(self, dupcheck=None, text=""):
        srsdict = {}
        dup_caseset = set()
        key_vals, have_null = self._check_datatype(*self.data, text)

        for key, value in key_vals:
            if dupcheck:
                dup_case = dupcheck.check(key, value)
                dupcheck.after(key, value)
                dup_caseset.add(dup_case)
            srsdict[key] = value

        return srsdict, have_null, dup_caseset, dupcheck


class SRSFunc:
    def merge_srs(self, files):
        if not files:
            files, encoding = CustomInput("SIMPLESRS").get_filelist()
        srs_dict = SRSEditor().merge(*files, encoding=encoding)

        return SRSFormat(srs_dict, 'merged-srs')

    def srsdict_to_sheet(self, srs_data=None):
        if not srs_data:
            filename = input("작업할 srs/simplesrs 파일의 경로를 입력해주세요.")
            encoding = MenuPreset().encode()
            srs_data, _ = SRSFile(filename, encoding).make_dict()
            sheetname = FileFilter().sep_filename(filename)
        else:
            sheetname = 'srs-sheet'

        result, _ = SRSConvert().make_srs_to_sheet(srs_data, sheetname)

        return result

    def make_srsfmt(self, key_dataset, val_dataset, dupcheck, dataname="", adv_opt=0, debug=False):
        """주어진 데이터셋(str list)을 바탕으로 SRSFormat 및 DupItemCheck 객체 반환"""
        text = dataname + " 내에서 " if dataname else ""

        if len(key_dataset) != len(val_dataset):
            print("%s특정 자료의 개수가 같지 않아 올바른 동작을 보장할 수 없습니다." % text)

        srsdict, have_null, dup_caseset, dupcheck = SRSMaker((key_dataset, val_dataset)).make_srsdict(dupcheck, text)

        if not srsdict:
            print("%s처리 가능한 데이터를 찾지 못했습니다." % text)
            return False

        srsdict, except_list = SRSEditor().advanced_filter(srsdict, adv_opt)

        dup_caseset.remove(0)
        if dupcheck and dupcheck.dup_dict and debug:
            print("%s중복된 케이스들이 발견되었습니다. 코드: " % dataname, dup_caseset)

        if have_null:
            if debug:
                print("%s일부 자료에서 공란이 확인되었습니다." % text)
            blank_list = [ [], [] ]
            for key, null_loc in have_null.items():
                null_loc -= 1
                if null_loc >= 0:
                    blank_list[null_loc].append(key)
            except_list.extend(blank_list)

        if except_list and debug:
            for cnt, excepts in enumerate(except_list):
                if cnt == 0: # 미번역 단어
                    text = "미번역된 단어 %d 개가 필터링되었습니다." % len(excepts)
                elif cnt == 1: # 한글자 단어
                    text = "한글자 단어 %d 개가 필터링되었습니다." % len(excepts)
                elif cnt == 2: # 원문 누락
                    text = "번역문 대비 원문 %d 개가 공란입니다." % len(excepts)
                elif cnt == 3: # 번역문 누락
                    text = "원문 대비 번역문 %d 개가 공란입니다." % len(excepts)
                if excepts: print(text)

        return SRSFormat(srsdict, dataname), dupcheck, except_list

    def exist_srsdict(self, srsname, encoding="UTF-8"):
        return SRSFile(srsname, encoding).make_dict()

    def build_srsdict(self, data_fm, data_to):
        return SRSMaker((data_fm, data_to)).make_srsdict()
