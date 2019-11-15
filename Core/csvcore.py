# CSV 기능 관련 모듈
import csv
from util import CommonSent, CustomInput,\
    DataFilter, InfoDict, LoadFile, MenuPreset


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
        self.list_csvdata = DataFilter().dup_filter(self.list_csvdata)


class CSVFunc:
    def import_all_CSV(self,mode_num=0): #TODO chara 대응방안 제기, StatusNum 기능 겷합
        print("추출을 시작합니다.")
        with LoadFile('csv_debug.log', 'UTF-8').readwrite() as debug_log:
            debug_log.write("오류코드 0xef는 UTF-8-sig, 다른 경우\
 cp932(일본어)나 cp949(한국어)로 시도하세요.\n")
            __error_check, __file_count = 0, 0
            user_input = CustomInput("CSV")
            target_dir = user_input.input_option(1)
            encode_type = MenuPreset().encode()
            csv_files = DataFilter().files_ext(target_dir, '.CSV')
            self.dic_assemble = InfoDict()
            for filename in csv_files:
                open_csv = CSVLoad(filename, encode_type)
                if mode_num <= 2:
                    if mode_num  == 0: # 구별없이 전부
                        option_tuple = (0,)
                    elif mode_num == 1: # chara 제외
                        if 'chara' in filename.lower():
                            continue
                        option_tuple = (0,)
                    elif mode_num == 2: # chara 만
                        if 'chara' in filename.lower():
                            option_tuple = (0,['NAME','CALLNAME','名前','呼び名'])
                        else: continue
                else:
                    if mode_num == 3: # srs 최적화 - 이름
                        if 'chara' in filename.lower():
                            option_tuple = (0,['NAME','CALLNAME','名前','呼び名'])
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
                        print("{}에서 {} 발생\n".format(
                            filename, UniDecode), file=debug_log)
                        __error_check += 1
                open_csv.dict_csvdata = DataFilter(
                ).erase_quote(open_csv.dict_csvdata, ';')
                self.dic_assemble.add_dict(filename,open_csv.dict_csvdata)
                __file_count += 1
            if __error_check != 0:
                print("""
                {}건 추출 도중 {}건의 인코딩 오류가 발생했습니다.\
                debug.log를 확인해주세요.
                """.format(__file_count, __error_check))
            else:
                print("{}건이 추출되었습니다.".format(__file_count))
                debug_log.write("오류가 발생하지 않았거나 파일이 덮어씌워졌습니다.")
        CommonSent.extract_finished()
        CommonSent.print_line()
        return self.dic_assemble
