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
            erb_translated_list = []
            for line in txt_text_list:
                splited_line = line.split()
                try:
                    if "!~" in splited_line[0]:
                        if "또는" in line:
                            line = line.replace("또는", "||")
                        if "이고" in line:
                            line = line.replace("이고","&&")
                        if "일 떄:" in line:
                            line = "IF "+line
                        erb_translated_list.append(line)
                    elif "/t" in line:
                        if "~아나타" in line or "~당신" in line:
                            line = line.replace("~아나타","%CALLNAME:MASTER%")
                            line = line.replace("~당신","%CALLNAME:MASTER%")
                        erb_translated_list.append(line)
                except IndexError: pass
            erb_export_opened.writelines(erb_translated_list)

    def import_erbtext_info(self,situation,context,cases):
        pass


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

    def make_tree(self):
        print("""
        ERB 내 조건문 구조를 트리 형태로 보여줍니다.
        되도록 적은 수의 ERB만을 포함시키는 편이 가독성이 높습니다.
        """)
        with LoadFile('ERBtree.txt').readwrite() as tree_txt:
            user_input = CustomInput("ERB")
            target_dir = user_input.input_option(1)
            encode_type = MenuPreset().encode()
            erb_files = DataFilter().files_ext(target_dir, '.ERB',1)
            for filename in erb_files:
                tree_txt.write("{}\n".format(filename))
                with LoadFile(filename,encode_type).readonly() as erb_opened:
                    for line in erb_opened:
                        pass


class ERBtextInfo(ERBWrite):
    def put_info(self, context, situation, *cases):
        self.context = context
        self.situation = situation
        self.case_count = 0
        self.case_list = []
        for case in cases:
            if 'CASE' in case:
                pass
            elif 'DATA' in case:
                pass
            else:
                case_count += 1
                self.case_list.append('\t'*case_count+case)
    def export_erbinfo(self):
        return self.situation, self.context, self.case_list


# 디버그용
if __name__ == '__main__':
    # ERBFunc().search_csv_var()
    origin_txt = ERBWrite('testtext.txt','utf-8-sig')
    while origin_txt.readonly():
        origin_txt.trans_erb()
