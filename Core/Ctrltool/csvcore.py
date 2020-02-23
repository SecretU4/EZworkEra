# CSV 기능 관련 모듈
import csv
from System.interface import StatusNum
from customdb import InfoDict
from util import CommonSent, DataFilter
from usefile import FileFilter, LoadFile, LogPreset, MenuPreset


class CSVLoad(LoadFile):
    def __init__(self,NameDir,EncodeType):
        super().__init__(NameDir,EncodeType)
        self.csv_reading = csv.reader(self.readonly())

    def core_csv(self, mode_num=0, Filter_list=None):
        self.dict_csvdata = {}
        self.list_csvdata = []
        for row_list in self.csv_reading:
            if not row_list: continue
            elif str(row_list[0]).strip().startswith(';'): continue
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
    def __init__(self):
        self.debug_log = LogPreset(1)

    def import_all_CSV(self,mode_num=0):
        """InfoDict 클래스를 받아 CSV 변수 자료형 생성
        
        {csv파일명:{csv변수명:숫자}} 또는 {csv파일명:{숫자:csv변수명}}
        """
        print("추출을 시작합니다.")
        csv_files, encode_type = FileFilter().get_filelist('CSV')
        self.dic_assemble = InfoDict(0)
        count_check = StatusNum(csv_files,'파일',self.debug_log.NameDir)
        count_check.how_much_there()
        for filename in csv_files:
            self.debug_log.write_loaded_log(filename)
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
                    self.debug_log.write_error_log(UniDecode,filename)
                    count_check.error_num += 1
            open_csv.dict_csvdata = DataFilter(
            ).erase_quote(open_csv.dict_csvdata, ';')
            self.dic_assemble.add_dict(filename,open_csv.dict_csvdata)
            count_check.how_much_done()
        if count_check.error_num > 0: self.debug_log.if_decode_error()
        CommonSent.extract_finished()
        CommonSent.print_line()
        self.debug_log.sucessful_done()
        return self.dic_assemble

    def single_csv_read(self,csvname,encode_type='UTF-8',opt=0):
        csv_data = CSVLoad(csvname,encode_type)
        self.debug_log.write_loaded_log(csvname)
        try:
            if opt in (0,1):
                csv_data.core_csv(opt)
                the_result = csv_data.dict_csvdata
            elif opt == 2:
                csv_data.core_csv()
                the_result = DataFilter().dup_filter(csv_data.list_csvdata)
        except UnicodeDecodeError as UniDecode:
            self.debug_log.if_decode_error()
            self.debug_log.write_error_log(UniDecode)
            the_result = None
        self.debug_log.sucessful_done()
        return the_result

    def make_csv_var_dict(self):
        """{csv변수명:[파일명,번호]} 형태 딕셔너리 제작"""
        print("csv 변수 대응 딕셔너리를 제작합니다.")
        csv_files, encode_type = FileFilter().get_filelist('CSV')
        count_check = StatusNum(csv_files,'파일',self.debug_log.NameDir)
        count_check.how_much_there()
        csvvar_dict = {}
        all_var_list = []
        dup_count = 0
        for csvname in csv_files:
            csv_data = CSVLoad(csvname,encode_type)
            self.debug_log.write_loaded_log(csvname)
            try:
                csv_data.core_csv(1) # {변수명:숫자}
                for var in csv_data.dict_csvdata.keys():
                    if var == '': continue
                    core_var = var
                    var = var.split(';')[0]
                    nospace_var = var.replace(' ','__')
                    all_var_list.append(var)
                    try:
                        if csvvar_dict.get(nospace_var):
                            dup_count = all_var_list.count(var) - 1
                            csvvar_dict['dup{}_{}'.format(
                                dup_count,nospace_var)] = [csvname,int(csv_data.dict_csvdata[core_var])]
                        else:
                            csvvar_dict[nospace_var] = [csvname,int(csv_data.dict_csvdata[core_var])]
                    except ValueError: continue
            except UnicodeDecodeError as UniDecode:
                self.debug_log.write_error_log(UniDecode,csvname)
                count_check.error_num += 1
            count_check.how_much_done()
        total_dup = len(all_var_list) - len(set(all_var_list))
        if dup_count != 0: print("{}건의 중복변수가 존재합니다. 추후 유의해주세요.".format(total_dup))
        if count_check.error_num > 0: self.debug_log.if_decode_error()
        CommonSent.extract_finished()
        CommonSent.print_line()
        self.debug_log.sucessful_done()
        return csvvar_dict
