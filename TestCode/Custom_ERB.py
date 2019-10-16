# ERB 관련 모듈
from customcore import CommonSent, CustomInput, DataFilter,\
                        LoadFile, MenuPreset
from custom_csv import _CSVLoad


class ERBLoad(LoadFile):
    def _make_context_list(self):
        with self.readonly() as erb_origin:
            self.erb_context_list = erb_origin.readlines()
            return self.erb_context_list

    def search_line(self,*args):
        self._make_context_list()
        self.targeted_list = []
        skip_switch = 0
        for line in self.erb_context_list:
            if skip_switch == 1:
                if '[SKIPEND]' in line: skip_switch = 0
                continue
            else:
                if '[SKIPSTART]' in line:
                    skip_switch = 1
                    continue
                for target in args:
                    if target in line:
                        self.targeted_list.append(line)
        return self.targeted_list
    
    def search_word(self,loc_num,*args):
        self._make_context_list()
        self.targeted_list = []
        for line in self.erb_context_list:
            line_word = line.split()
            for target in args:
                if target in line_word[loc_num]:
                    self.targeted_list.append(line_word[loc_num])
        return self.targeted_list


class ERBWrite(LoadFile):
    def export_erb(self):
        self.erb_exporting = LoadFile('trans_{0}.erb'.format(
            self.NameDir),self.EncodType)

    def trans_erb(self): # 작업중
        self.export_erb()
        with self.readonly() as txt_origin:
            txt_text_list = txt_origin.readlines()
        with self.erb_exporting.readwrite() as erb_export_opened:
            for line in txt_text_list:
                splited_line = line.split()
                try:
                    if "~!" in splited_line[0]:
                        pass
                    elif "~아나타" in line or "~당신" in line:
                        line = line.replace("~아나타","%CALLNAME:MASTER%")
                        line = line.replace("~당신","%CALLNAME:MASTER%")
                except IndexError:
                    continue
            erb_export_opened.writelines()


class ERBFunc:
    def extract_printfunc(self):
        print("PRINT/DATA FORM 구문의 추출을 시작합니다.")
        with LoadFile('debuglog.txt', 'UTF-8').readwrite() as debug_log:
            user_input = CustomInput("ERB")
            target_dir = user_input.input_option(1)
            encode_type = MenuPreset().encode()
            erb_files = DataFilter().files_ext(target_dir, '.ERB')
            for filename in erb_files:
                erb_opened = ERBLoad(filename, encode_type)
                printfunc_list = erb_opened.search_line(
                                'PRINTFORM', 'DATAFORM')
                debug_log.write(filename)
                debug_log.writelines(printfunc_list)
        print("추출이 완료되었습니다.")
        CommonSent.print_line()

    def search_csv_var(self):
        print("ERB 파일에서 사용된 CSV 변수목록을 추출합니다.\
현재 기능의 의미가 별로 없는 상황입니다.")
        with LoadFile('debug.log','UTF-8').readwrite() as debug_log:
            var_list = _CSVLoad('CSVfnclist.csv','UTF-8-SIG').info_data_csv()
            user_input = CustomInput("ERB")
            target_dir = user_input.input_option(1)
            encode_type = MenuPreset().encode()
            erb_files = DataFilter().files_ext(target_dir, '.ERB')
            files_count = len(erb_files)
            file_count = 0
            level_show_list = list(map(lambda x: x*int(round(files_count)/4
                                                    ), list(range(1,5))))
            if len(erb_files) > 500:
                level_show_list = list(map(lambda x: x*int(round(files_count)/10
                                                    ),list(range(1,11))))
            for filename in erb_files:
                debug_log.write("{}\n".format(filename))
                erb_opened = ERBLoad(filename, encode_type)
                var_context_list = erb_opened.search_line(*var_list)
                if bool(var_context_list) is True:
                    filtered_con_list = DataFilter().dup_filter(var_context_list)
                    debug_log.writelines(filtered_con_list)
                file_count +=1
                if file_count in level_show_list:
                    print("{}/{} 완료".format(file_count,len(erb_files)))
        print("변수 목록이 작성되었습니다.")
        CommonSent.print_line()
# 디버그용
if __name__ == '__main__':
    # ERBFunc().search_csv_var()
    origin_txt = ERBWrite('testtext.txt','utf-8')
    while origin_txt.readonly():
        origin_txt.trans_erb()