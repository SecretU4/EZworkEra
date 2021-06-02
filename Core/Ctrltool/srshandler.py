# simplesrs, srs 관련 처리 모듈

from customdb import SheetInfo
from usefile import LoadFile
from util import DataFilter, DupItemCheck


class SRSFile:
    """이미 존재하는 srs계열 파일의 처리 관련 클래스"""
    def __init__(self, srsname):
        self.srsname = srsname
        self.the_bulk = LoadFile(srsname).make_bulklines()
        self.srs_bulk = DataFilter().strip_filter(self.the_bulk)

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

    def make_dict(self, head_flag=True, srs_type=None):
        if srs_type == None:
            srs_type = self.check_srstype()

        if srs_type == 0: # srs 관련 양식이 아님
            raise TypeError
        elif srs_type == 2: # srs는 HEAD 미지원
            context_flag = False
            head_flag = False

        result_dict = dict()
        dup_check = DupItemCheck()
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


class SRSConvert(SRSFile):
    """srs 파일 내용을 다른 형태로 변환하는 클래스"""
    def make_srs_to_sheet(self, sheetname="srs-sheet", srs_type=None):
        result_sheet = SheetInfo()
        result_sheet.add_sheet(sheetname, ['orig_name', 'trans_name'])
        srs_dict, dup_check = self.make_dict(srs_type=srs_type)
        for key, value in srs_dict.items():
            result_sheet.add_row(sheetname, orig_name=key, trans_name=value)

        if dup_check.dup_dict:
            print("중복되는 요소들이 발견되었습니다.")

        return result_sheet, dup_check.dup_dict


class SRSEditor:
    """srs 내용을 편집하는 클래스"""
    def merge(self, *files):
        result_dict = dict()
        for filename in files:
            srs_dict, dup_check = SRSFile(filename).make_dict()
            result_dict.update(srs_dict)

        if dup_check.dup_dict:
            print("%s 내부에서 중복되는 요소들이 발견되었습니다." % filename)

        return result_dict


class SRSFunc:
    pass