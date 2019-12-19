# CSV 기능 관련 모듈
import csv
from System.interface import StatusNum
from customdb import InfoDict
from util import CommonSent, DataFilter
from usefile import FileFilter, LoadFile, MakeLog, MenuPreset


class CSVLoad(LoadFile):
    def __init__(self,NameDir,EncodeType):
        super().__init__(NameDir,EncodeType)
        self.csv_reading = csv.reader(self.readonly())

    def core_csv(self, mode_num=0, Filter_list=None):
        self.dict_csvdata = {}
        self.list_csvdata = []
        for row_list in self.csv_reading:
            try:
                data_1 = str(row_list[0]).strip()
                data_2 = str(row_list[1]).strip()
                if mode_num == 0:
                    select_dataset = data_1
                    another_dataset = data_2
                elif mode_num == 1:
                    select_dataset = data_2
                    another_dataset = data_1
            except IndexError: continue
            self.list_csvdata.extend([data_1, data_2])
            if Filter_list == None:
                self.dict_csvdata[select_dataset] = another_dataset
            else:
                if select_dataset in Filter_list:
                    self.dict_csvdata[select_dataset] = another_dataset


class CSVFunc:
    def import_all_CSV(self,mode_num=0):
        print("추출을 시작합니다.")
        debug_log = MakeLog('csv_debug.log')
        debug_log.first_log()
        debug_log.write_log("""오류코드 0xef는 UTF-8-sig,
        다른 경우 cp932(일본어)나 cp949(한국어)로 시도하세요.\n
        """)
        csv_files, encode_type = FileFilter().get_filelist('CSV')
        self.dic_assemble = InfoDict()
        count_check = StatusNum(csv_files,'파일',debug_log.NameDir)
        count_check.how_much_there()
        for filename in csv_files:
            open_csv = CSVLoad(filename, encode_type)
            if mode_num <= 2:
                if mode_num  == 0: # 구별없이 전부
                    option_tuple = (0,)
                elif mode_num == 1: # chara 제외
                    if 'chara' in filename.lower(): continue
                    option_tuple = (0,)
                elif mode_num == 2: # 문자/숫자 변환 - {변수:숫자} 형태(chara 제외)
                    if 'chara' in filename.lower(): continue
                    option_tuple = (1,)
                else:
                    if mode_num == 3: # srs 최적화 - 이름
                        if 'chara' in filename.lower():
                            option_tuple = (0,['CALLNAME','呼び名'])
                        elif 'name' in filename.lower():
                            option_tuple = (0,)
                        else: continue
                    elif mode_num == 4: # srs 최적화 - 변수
                        if 'chara' in filename.lower():
                            continue
                        elif 'variable' in filename.lower():
                            continue
                        elif 'name' in filename.lower():
                            continue
                        elif 'replace' in filename.lower():
                            continue
                        else: option_tuple = (0,)
                with open_csv.readonly():
                    try:
                        open_csv.core_csv(*option_tuple)
                    except UnicodeDecodeError as UniDecode:
                        debug_log.write_error_log(UniDecode,filename)
                        count_check.error_num += 1
                open_csv.dict_csvdata = DataFilter(
                ).erase_quote(open_csv.dict_csvdata, ';')
                self.dic_assemble.add_dict(filename,open_csv.dict_csvdata)
                count_check.how_much_done()
        CommonSent.extract_finished()
        CommonSent.print_line()
        return self.dic_assemble

    def implement_csv_datalist(self,csvname,encode_type='UTF-8'):
        csv_data = CSVLoad(csvname,encode_type)
        csv_data.core_csv()
        csv_data.list_csvdata = DataFilter().dup_filter(csv_data.list_csvdata)
        return csv_data.list_csvdata

    def make_csv_var_dict(self):
        """{csv변수명:[파일명,번호]} 형태 딕셔너리 제작"""
        print("csv 변수 대응 딕셔너리를 제작합니다.")
        debug_log = MakeLog('csv_debug.log')
        debug_log.first_log()
        debug_log.write_log("""오류코드 0xef는 UTF-8-sig,
        다른 경우 cp932(일본어)나 cp949(한국어)로 시도하세요.\n
        """)
        csv_files, encode_type = FileFilter().get_filelist('CSV')
        count_check = StatusNum(csv_files,'파일',debug_log.NameDir)
        count_check.how_much_there()
        csvvar_dict = {}
        all_var_list = []
        dup_count = 0
        for csvname in csv_files:
            csv_data = CSVLoad(csvname,encode_type)
            try:
                csv_data.core_csv(1) # {변수명:숫자}
                for var in csv_data.dict_csvdata.keys():
                    if var == '': continue
                    var = var.split(';')[0]
                    nospace_var = var.replace(' ','__')
                    all_var_list.append(var)
                    try:
                        if csvvar_dict.get(nospace_var):
                            dup_count = all_var_list.count(var) - 1
                            csvvar_dict['dup{}_{}'.format(
                                dup_count,nospace_var)] = [csvname,int(csv_data.dict_csvdata[var])]
                        else:
                            csvvar_dict[nospace_var] = [csvname,int(csv_data.dict_csvdata[var])]
                    except ValueError: continue
            except UnicodeDecodeError as UniDecode:
                debug_log.write_error_log(UniDecode,csvname)
                count_check.error_num += 1
            count_check.how_much_done()
        total_dup = len(all_var_list) - len(set(all_var_list))
        if dup_count != 0: print("{}건의 중복변수가 존재합니다. 추후 유의해주세요.".format(total_dup))
        CommonSent.extract_finished()
        CommonSent.print_line()
        return csvvar_dict
