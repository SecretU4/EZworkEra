# simplesrs, srs 관련 처리 모듈

from customdb import SheetInfo, SRSFormat
from usefile import FileFilter, LoadFile, MenuPreset
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


class SRSFunc:
    def merge_srs(self, files):
        if not files:
            files, encoding = FileFilter().get_filelist("SIMPLESRS")
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

    def make_srsfmt(self, key_dataset, val_dataset, total_data={}, dup_data={}, dataname="", adv_opt=0, pnt_flag=False):
        """주어진 데이터셋(str list)을 바탕으로 SRSFormat 및 DupItemCheck 객체 반환"""
        if len(key_dataset) != len(val_dataset):
            print("특정 자료의 개수가 같지 않아 올바른 동작을 보장할 수 없습니다.")

        dupcheck = DupItemCheck(total_data, dup_data)
        srsdict = {}
        dup_case = set()
        for key, value in zip(key_dataset, val_dataset):
            dup_case.add(dupcheck.check(key, value))
            srsdict[key] = value
            dupcheck.after(key, value)

        srsdict, filtered = SRSEditor().advanced_filter(srsdict, adv_opt)

        if dupcheck.dup_dict:
            print("중복된 케이스들이 발견되었습니다. 코드: ", dup_case)

        text = dataname + " 내에서 " if dataname else ""
        for cnt, flt_list in enumerate(filtered):
            if cnt == 0: # 미번역 단어
                text += "미번역된 단어 %d 개가 필터링되었습니다." % len(flt_list)
            elif cnt == 1: # 한글자 단어
                text += "한글자 단어 %d 개가 필터링되었습니다." % len(flt_list)
            if flt_list and pnt_flag:
                print(text)

        return SRSFormat(srsdict, dataname), dupcheck, filtered

    def make_srsdict(self, srsname, encoding="UTF-8"):
        return SRSFile(srsname, encoding).make_dict()
