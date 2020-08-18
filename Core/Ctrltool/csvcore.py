# CSV 기능 관련 모듈
import csv
import logging
import logging.config
from System.interface import StatusNum
from customdb import InfoDict
from util import CommonSent, DataFilter
from usefile import FileFilter, LoadFile, MenuPreset


class CSVLoad(LoadFile):
    def __init__(self, NameDir, EncodeType):
        super().__init__(NameDir, EncodeType)
        self.csv_reading = csv.reader(self.readonly())

    def core_csv(self, mode_num=0, Filter_list=None):
        self.dict_csvdata = {}
        self.list_csvdata = []
        for row_list in self.csv_reading:
            if not row_list:
                continue
            elif str(row_list[0]).strip().startswith(";"):
                continue
            try:
                data_1 = str(row_list[0]).strip()
                data_2 = str(row_list[1]).strip()
                if mode_num == 0:
                    select_dataset = data_1
                    another_dataset = data_2
                elif mode_num == 1:
                    select_dataset = data_2
                    another_dataset = data_1
            except IndexError:
                continue
            self.list_csvdata.extend([data_1, data_2])
            if Filter_list == None:
                self.dict_csvdata[select_dataset] = another_dataset
            else:
                if select_dataset in Filter_list:
                    self.dict_csvdata[select_dataset] = another_dataset


class CSVFunc:

    logging.config.fileConfig('Core\\logging.conf')
    logger = logging.getLogger('CSVFunc')

    def import_all_CSV(self, mode_num=0, csv_files=None, encode_type=None):
        """InfoDict 클래스를 받아 CSV 변수 자료형 생성

        {csv파일명:{csv변수명:숫자}} 또는 {csv파일명:{숫자:csv변수명}}
        """
        print("추출을 시작합니다.")
        if not csv_files or not encode_type:
            csv_files, encode_type = FileFilter().get_filelist("CSV")
        self.dic_assemble = InfoDict(0)
        count_check = StatusNum(csv_files, "파일", self.logger.handlers[1].baseFilename)
        count_check.how_much_there()

        for filename in csv_files:
            deny_flag = 0
            if mode_num <= 2:  # 파일 이름 따른 처리 여부 구분
                if mode_num == 0:  # 구별없이 전부
                    option_tuple = (0,)
                elif mode_num == 1:  # chara 제외
                    if "chara" in filename.lower():
                        deny_flag = 1
                    option_tuple = (0,)
                elif mode_num == 2:  # 문자/숫자 변환 - {변수:숫자} 형태(chara 제외)
                    if "chara" in filename.lower():
                        deny_flag = 1
                    option_tuple = (1,)
            else:
                if mode_num == 3:  # srs 최적화 - 이름
                    if "chara" in filename.lower():
                        option_tuple = (0, ["CALLNAME", "呼び名"])
                    elif "name" in filename.lower():
                        option_tuple = (0,)
                    else:
                        deny_flag = 1
                elif mode_num == 4:  # srs 최적화 - 변수
                    if "chara" in filename.lower():
                        deny_flag = 1
                    elif "variable" in filename.lower():
                        deny_flag = 1
                    elif "name" in filename.lower():
                        deny_flag = 1
                    elif "replace" in filename.lower():
                        deny_flag = 1
                    else:
                        option_tuple = (0,)

            if not deny_flag:
                csvdata_dict = self.single_csv_read(filename, encode_type, *option_tuple)

                if csvdata_dict:
                    self.dic_assemble.add_dict(filename, csvdata_dict)
                else: # 인식되지 않은 경우 infodict에 추가되지 않음
                    count_check.error_num += 1

            count_check.how_much_done()

        if count_check.error_num > 0:
            self.logger.warning('인코딩 에러 발생')
        CommonSent.extract_finished()
        CommonSent.print_line()
        self.logger.info('import_all_csv 작업 완료됨')
        return self.dic_assemble

    def single_csv_read(self, csvname, encode_type="UTF-8", opt=0, filter_list=None):
        """csv 파일을 읽어 dict형이나 list형을 불러옴.
        opt 0: {0행:1행}, 1: {1행:0행}, 2:[1행1열,1행2열,...]
        """
        csv_data = CSVLoad(csvname, encode_type)
        self.logger.debug('%s loaded' % csvname)
        try:
            if opt in (0, 1):
                csv_data.core_csv(opt)
                the_result = DataFilter().erase_quote(csv_data.dict_csvdata)
            elif opt == 2:
                csv_data.core_csv()
                the_result = DataFilter().dup_filter(csv_data.list_csvdata)
        except UnicodeDecodeError as UniDecode:
            if opt == 2:
                self.logger.warning('인코딩 에러 발생')
            self.logger.warning('%s @ %s' % (UniDecode, csvname))
            the_result = None

        return the_result

    def make_csv_var_dict(self, csv_files=None, encode_type=None):
        """{csv변수명:[파일명,번호]} 형태 딕셔너리 제작"""
        print("csv 변수 대응 딕셔너리를 제작합니다.")
        if not csv_files or not encode_type:
            csv_files, encode_type = FileFilter().get_filelist("CSV")

        count_check = StatusNum(csv_files, "파일", self.logger.handlers[1].baseFilename)
        count_check.how_much_there()
        csvvar_dict = {}
        all_var_list = []
        dup_count = 0

        for csvname in csv_files:
            csvdata_dict = self.single_csv_read(csvname, encode_type, 1)  # {변수명:숫자}
            if csvdata_dict == None:
                count_check.error_num += 1
                continue

            for var in csvdata_dict.keys():
                if var == "":
                    continue
                core_var = var
                var = var.split(";")[0]
                nospace_var = var.replace(" ", "__")
                all_var_list.append(var)
                try:
                    if csvvar_dict.get(nospace_var):
                        dup_count = all_var_list.count(var) - 1
                        csvvar_dict["dup{}_{}".format(dup_count, nospace_var)] = [
                            csvname,
                            int(csvdata_dict[core_var]),
                        ]
                    else:
                        csvvar_dict[nospace_var] = [csvname, int(csvdata_dict[core_var])]
                except ValueError:
                    continue
            count_check.how_much_done()

        total_dup = len(all_var_list) - len(set(all_var_list))
        if dup_count != 0:
            print("{}건의 중복변수가 존재합니다. 추후 유의해주세요.".format(total_dup))
        if count_check.error_num > 0:
            self.logger.warning('인코딩 에러 발생')

        CommonSent.extract_finished()
        CommonSent.print_line()
        self.logger.info('make_csv_var_dict 작업 완료됨')
        return csvvar_dict
