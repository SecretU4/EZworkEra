# CSV 기능 관련 모듈
import csv
from customcore import CommonSent, CustomInput,\
                    DataFilter, LoadFile, MenuPreset


class _CSVLoad(LoadFile):
    def _start_csv(self):
        self.csv_reading = csv.reader(self.readonly())

    def core_csv(self, select_num, Filter_info):
        self._start_csv()
        self.data_dict = {}
        for row_list in self.csv_reading:
            try:
                data_1 = str(row_list[0]).strip()
                data_2 = str(row_list[1]).strip()
                if select_num == 0:
                    self.data_dict[data_1] = data_2
                    continue
                elif select_num == 1:
                    select_dataset = data_1
                    another_dataset = data_2
                elif select_num == 2:
                    select_dataset = data_2
                    another_dataset = data_1
            except IndexError: continue
            if select_dataset == Filter_info:
                self.data_dict[select_dataset] = another_dataset

    def info_data_CSV(self):
        self._start_csv()
        info_data_list = []
        for row_list in self.csv_reading:
            try:
                data1 = str(row_list[0])
                data2 = str(row_list[1])
            except IndexError: continue
            info_data_list.append(data1)
            info_data_list.append(data2)
        data_filtered = DataFilter().dup_filter(info_data_list)
        return data_filtered


class CSVFunc:
    def import_all_CSV(self):
        print("추출을 시작합니다.")
        with LoadFile('debug.txt', 'UTF-8').readwrite() as debug_txt:
            with LoadFile('debuglog.txt', 'UTF-8').readwrite() as debug_log:
                debug_log.write(
                    "오류코드 0xef는 UTF-8-sig, 다른 경우 \
                    cp932(일본어)나 cp949(한국어)로 시도하세요.\n")
                _error_check, _file_count = 0, 0
                user_input = CustomInput("CSV")
                target_dir = user_input.input_option(1)
                encode_type = MenuPreset().encode()
                csv_files = DataFilter().files_ext(target_dir, '.CSV')
                for filename in csv_files:
                    open_csv = _CSVLoad(filename, encode_type)
                    with open_csv.readonly():
                        try:
                            open_csv.core_csv(0, 0)
                        except UnicodeDecodeError as UniDecode:
                            print("{}에서 {} 발생\n".format(
                                filename, UniDecode), file=debug_log)
                            _error_check += 1
                    open_csv.data_dict = DataFilter(
                        ).erase_quote(open_csv.data_dict, ';')
                    print('{0}\n{1}\n'.format(
                        filename, open_csv.data_dict), file=debug_txt)
                    _file_count += 1
                if _error_check != 0:
                    print("{}건 추출 도중 {}건의 인코딩 오류가 발생했습니다.\
                        debuglog.txt를 확인해주세요.".format(_file_count, _error_check))
                else:
                    print("{}건이 추출되었습니다.".format(_file_count))
                    debug_log.write("오류가 발생하지 않았거나 덮어씌워졌습니다.")
        CommonSent.extract_finished()
