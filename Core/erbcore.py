# ERB 관련 모듈
from util import CommonSent, CustomInput, DataFilter,\
                        LoadFile, MenuPreset, StatusNum
from csvcore import CSVLoad

class ERBMetaInfo:
    def __init__(self):
        self.linelist = []
        self.if_level = 0
        self.case_level = 0
        self.case_count = 0

    def add_line_list(self,line):
        self.linelist.append([self.if_level,self.case_level,self.case_count,line])


class ERBLoad(LoadFile):
    def __make_bulk_lines(self):
        with self.readonly() as erb_origin:
            self.erb_context_list = erb_origin.readlines()
            return self.erb_context_list

    def make_metainfo_lines(self,option_num=0): # 0: 전부 1: 기능관련만
        self.command_count = 0
        skip_start = 0
        erb_info = ERBMetaInfo()
        with self.readonly() as erb_opened:
            for line in erb_opened:
                line = line.strip()
                if line.startswith(';') == True: # 주석문
                    if option_num == 1:
                        continue
                    erb_info.add_line_list(line)
                elif '[SKIPEND]' in line:
                    skip_start = 0
                    erb_info.add_line_list(line)
                    continue
                elif skip_start == 1: continue
                elif '[SKIPSTART]' in line:
                    skip_start = 1
                    erb_info.add_line_list(line)
                    continue
                elif 'PRINT' in line:
                    if 'PRINTDATA' in line:
                        erb_info.add_line_list(line)
                        erb_info.case_level += 1
                    else:
                        if option_num == 1:
                            continue
                        erb_info.add_line_list(line)
                    continue
                elif 'IF' in line:
                    if 'ENDIF' in line:
                        erb_info.if_level -= 1
                        erb_info.add_line_list(line)
                    elif line.startswith('IF') == True:
                        erb_info.add_line_list(line)
                        erb_info.if_level += 1
                    elif 'ELSEIF' in line:
                        erb_info.if_level -= 1
                        erb_info.add_line_list(line)
                        erb_info.if_level += 1
                    elif 'SIF' in line: erb_info.add_line_list(line)
                    continue
                elif erb_info.case_level != 0: # 케이스 내부 돌 때
                    if 'CASE' in line:
                        if 'SELECTCASE' in line:
                            erb_info.case_level += 1
                            erb_info.add_line_list(line)
                        elif line.startswith('CASE') == True:
                            erb_info.case_count += 1
                            if option_num == 1: continue
                            erb_info.add_line_list(line)
                        continue
                    elif 'DATA' in line:
                        if 'DATAFORM' in line :
                            if option_num == 1: continue
                            erb_info.add_line_list(line)
                        elif 'DATALIST' in line :
                            erb_info.case_count += 1
                            if option_num == 1:
                                erb_info.case_level += 1
                                continue
                            erb_info.add_line_list(line)
                            erb_info.case_level += 1
                        elif 'PRINTDATA' in line:
                            erb_info.case_level += 1
                            erb_info.add_line_list(line)
                            print("분기문 안에 분기문이 있습니다.")
                        elif 'ENDDATA' in line:
                            erb_info.case_level -= 1
                            line = line + ' ;{}개의 케이스 존재'.format(erb_info.case_count)
                            erb_info.case_count = 0
                            erb_info.add_line_list(line)
                        continue
                    elif 'END' in line:
                        if 'ENDSELECT' in line:
                            erb_info.case_level -= 1
                            line = line + ' ;{}개의 케이스 존재'.format(erb_info.case_count)
                            erb_info.case_count = 0
                            erb_info.add_line_list(line)
                        elif 'ENDLIST' in line :
                            erb_info.case_level -= 1
                            if option_num == 1: continue
                            erb_info.add_line_list(line)
                        continue
                elif 'SELECTCASE' in line:
                    erb_info.add_line_list(line)
                    erb_info.case_level += 1
                elif line.startswith('ELSE') == True:
                    erb_info.if_level -= 1
                    erb_info.add_line_list(line)
                    erb_info.if_level += 1
                elif line.startswith('RETURN') == True:
                    erb_info.add_line_list(line)
                elif line.startswith('GOTO') == True:
                    erb_info.add_line_list(line)
                elif line.startswith('LOCAL') == True:
                    erb_info.add_line_list(line)
                elif line.startswith('$') == True:
                    erb_info.add_line_list(line)
                elif line.startswith('@') == True:
                    self.command_count += 1
                    erb_info.add_line_list(line)
                else:
                    if option_num == 1: continue
                    erb_info.add_line_list(line)
        return erb_info.linelist

    def search_line(self,*args,except_args=None):
        self.__make_bulk_lines()
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
                elif except_args != None:
                    for except_arg in except_args:
                        if except_arg in line: continue
                for target in args:
                    if target in line:
                        self.targeted_list.append(line)
        return self.targeted_list

    def search_word(self,loc_num,*args):
        self.__make_bulk_lines()
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
            self.NameDir),self.EncodeType)

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
                        if "일떄:" in line:
                            line = "IF "+line
                        erb_translated_list.append(line)
                    elif "\t" in line:
                        if "~아나타" in line or "~당신" in line:
                            line = line.replace("~아나타","%CALLNAME:MASTER%")
                            line = line.replace("~당신","%CALLNAME:MASTER%")
                        erb_translated_list.append(line)
                except IndexError: pass
            erb_export_opened.writelines(erb_translated_list)

    def import_erbtext_info(self,situation,context,cases):
        pass


class ERBFilter:
    def indent_maker(self,target_metalines):
        self.filtered_lines = []
        for line in target_metalines:
                if_level, case_level, _, context = line
                self.filtered_lines.append('{}{}{}\n'.format('\t'*if_level,
                    '\t'*case_level,context))
        if self.filtered_lines == []: print("결과물이 없습니다.")
        return self.filtered_lines


class ERBFunc:
    def extract_printfunc(self):
        print("PRINT/DATAFORM 구문의 추출을 시작합니다.")
        with LoadFile('debuglog.txt', 'UTF-8').readwrite() as debug_log:
            user_input = CustomInput("ERB")
            target_dir = user_input.input_option(1)
            encode_type = MenuPreset().encode()
            erb_files = DataFilter().files_ext(target_dir, '.ERB')
            file_count_check = StatusNum(erb_files,'파일')
            file_count_check.how_much_there()
            for filename in erb_files:
                erb_opened = ERBLoad(filename, encode_type)
                printfunc_list = erb_opened.search_line(
                        'PRINT', 'DATAFORM',except_args=['PRINTDATA'])
                for line in printfunc_list:
                    if len(line.split()) == 1:
                        printfunc_list.remove(line)
                debug_log.write(filename)
                debug_log.writelines(printfunc_list)
                file_count_check.how_much_done()
        print("추출이 완료되었습니다.")
        CommonSent.print_line()

    def search_csv_var(self):
        print("ERB 파일에서 사용된 CSV 변수목록을 추출합니다.")
        with LoadFile('debug.log', 'UTF-8').readwrite() as debug_log:
            csv_fncdata = CSVLoad('CSVfnclist.csv','UTF-8-SIG')
            csv_fncdata.core_csv()
            var_list = csv_fncdata.list_csvdata
            user_input = CustomInput("ERB")
            target_dir = user_input.input_option(1)
            encode_type = MenuPreset().encode()
            erb_files = DataFilter().files_ext(target_dir, '.ERB')
            file_count_check = StatusNum(erb_files,'파일')
            file_count_check.how_much_there()
            for filename in erb_files:
                debug_log.write("{}\n".format(filename))
                erb_opened = ERBLoad(filename, encode_type)
                var_context_list = erb_opened.search_line(*var_list,except_args=['name'])
                if bool(var_context_list) is True:
                    filtered_con_list = DataFilter().dup_filter(var_context_list)
                    debug_log.writelines(filtered_con_list)
                file_count_check.how_much_done()
        print("변수 목록이 작성되었습니다.")
        CommonSent.print_line()

    def remodel_indent(self,option_num=None,target_metalines=None):
        self.result_lines = []
        if target_metalines == None:
            user_input = CustomInput("ERB")
            target_dir = user_input.input_option(1)
            num = MenuPreset().yesno("하위폴더까지 포함해 진행하시겠습니까?")
            encode_type = MenuPreset().encode()
            ERB_files = DataFilter().files_ext(target_dir, '.ERB',num)
            for filename in ERB_files:
                open_erb = ERBLoad(filename,encode_type)
                lines = open_erb.make_metainfo_lines(option_num)
                lines.insert(0,[0,0,0,";{}에서 불러옴".format(filename)])
                self.result_lines.extend(ERBFilter().indent_maker(lines))
        else:
            print("특정 데이터셋으로 작업합니다.")
            self.result_lines = ERBFilter().indent_maker(target_metalines)
        return self.result_lines


# 디버그용
if __name__ == '__main__':
    # testlines = ERBFunc().remodel_indent(option_num=1)
    # with LoadFile('Resultfiles/test.txt').readwrite() as TEST:
    #     TEST.writelines(testlines)
    pass