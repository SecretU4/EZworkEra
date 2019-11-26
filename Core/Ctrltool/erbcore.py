# ERB 관련 모듈
from Core.customdb import ERBMetaInfo, InfoDict
from Core.usefile import FileFilter, LoadFile
from Core.util import CommonSent, DataFilter, MakeLog
from Core.System.interface import MenuPreset, StatusNum
from . import CSVFunc

class ERBLoad(LoadFile):
    def make_bulk_lines(self):
        with self.readonly() as erb_origin:
            self.erb_context_list = erb_origin.readlines()
            return self.erb_context_list

    def search_line(self,*args,except_args=None):
        self.make_bulk_lines()
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
        self.make_bulk_lines()
        self.targeted_list = []
        for line in self.erb_context_list:
            line_word = line.split()
            for target in args:
                if target in line_word[loc_num]:
                    self.targeted_list.append(line_word[loc_num])
        return self.targeted_list


class ERBWrite(LoadFile):
    def __init__(self,NameDir,EncodeType):
        super().__init__(NameDir,EncodeType)

    def txt_to_metalines(self): #TODO 구상 번역기
        with self.readonly() as txt_origin:
            txt_text_list = txt_origin.readlines()
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
                    if "(아나타)" in line or "(당신)" in line:
                        line = line.replace("(아나타)","%CALLNAME:MASTER%")
                        line = line.replace("(당신)","%CALLNAME:MASTER%")
                    erb_translated_list.append(line)
            except IndexError: pass
            erb_metalines = ERBFilter().make_metainfo_lines(erb_translated_list,0,self.NameDir)
        return erb_metalines.linelist # list형 line

    def import_erbtext_info(self,situation,context,cases):
        pass


class ERBFilter:
    def indent_maker(self,target_metalines): # metaline을 들여쓰기된 lines로 만듦
        self.filtered_lines = []
        for line in target_metalines:
                if_level, case_level, _, context = line
                self.filtered_lines.append('{}{}{}\n'.format('\t'*if_level,
                    '\t'*case_level,context))
        if self.filtered_lines == []:
            print("결과물이 없습니다.")
            return None
        return self.filtered_lines

    def make_metainfo_lines(self,bulk_lines,option_num=0,target_name=None): # 0: 전부 1: 기능관련만
        self.command_count = 0
        skip_start = 0
        erb_info = ERBMetaInfo()
        erb_log = MakeLog('erb_debug.log')
        erb_log.first_log(target_name)
        for line in bulk_lines:
            line = line.strip()
            if '[SKIPEND]' in line:
                skip_start = 0
                erb_info.add_line_list(line)
                continue
            elif skip_start == 1: continue
            elif line.startswith(';') == True: # 주석문
                if option_num == 1: continue
                erb_info.add_line_list(line)
                continue
            elif '[SKIPSTART]' in line:
                skip_start = 1
                erb_info.add_line_list(line)
                continue
            elif 'PRINT' in line:
                if 'PRINTDATA' in line:
                    erb_info.add_line_list(line)
                    erb_info.case_level += 1
                else:
                    if option_num == 1: continue
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
                else: erb_log.write_error_log('미상정',line)
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
                        if erb_info.case_count == 1: erb_info.case_level += 1
                    else: erb_log.write_error_log('미상정',line)
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
                    else: erb_log.write_error_log('미상정',line)
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
                    else: erb_log.write_error_log('미상정',line)
                    continue
                else: pass
            if 'SELECTCASE' in line:
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
                erb_log.write_error_log('미상정',line)
        return erb_info


class ERBFunc:
    def __init__(self):
        self.result_infodict = InfoDict()

    def extract_printfunc(self):
        print("PRINT/DATAFORM 구문의 추출을 시작합니다.")
        erb_files, encode_type = FileFilter().get_filelist('ERB')
        file_count_check = StatusNum(erb_files,'파일')
        file_count_check.how_much_there()
        for filename in erb_files:
            bulk_lines = ERBLoad(filename, encode_type)
            printfunc_list = bulk_lines.search_line(
                    'PRINT', 'DATAFORM',except_args=['PRINTDATA'])
            for line in printfunc_list:
                if len(line.split()) == 1:
                    printfunc_list.remove(line)
            self.result_infodict.add_dict(filename,printfunc_list)
            file_count_check.how_much_done()
        CommonSent.extract_finished()
        return self.result_infodict # {파일명:lines} 형태가 포함된 infodict

    def search_csv_var(self,var_list=None):
        print("ERB 파일에서 사용된 CSV 변수목록을 추출합니다.")
        if var_list == None:
            var_list = CSVFunc().implement_csv_datalist('CSVfnclist.csv')
        erb_files, encode_type = FileFilter().get_filelist('ERB')
        file_count_check = StatusNum(erb_files,'파일')
        file_count_check.how_much_there()
        for filename in erb_files:
            filtered_con_list = None
            bulk_lines = ERBLoad(filename, encode_type)
            var_context_list = bulk_lines.search_line(*var_list,except_args=['name'])
            if bool(var_context_list) is True:
                filtered_con_list = DataFilter().dup_filter(var_context_list)
                self.result_infodict.add_dict(filename,filtered_con_list)
            file_count_check.how_much_done()
        CommonSent.extract_finished()
        return self.result_infodict # {파일명:lines} 형태가 포함된 infodict

    def remodel_indent(self,metainfo_option_num=None,target_metalines=None):
        print("들여쓰기를 자동 교정하는 유틸리티입니다.")
        if target_metalines == None:
            erb_files, encode_type = FileFilter().get_filelist('ERB')
            file_count_check = StatusNum(erb_files,'파일')
            file_count_check.how_much_there()
            for filename in erb_files:
                erb_bulk = ERBLoad(filename,encode_type).make_bulk_lines()
                lines = ERBFilter.make_metainfo_lines(
                    erb_bulk,metainfo_option_num,filename).linelist
                lines.insert(0,[0,0,0,";{}에서 불러옴\n".format(filename)])
                self.result_infodict.add_dict(filename,ERBFilter().indent_maker(lines))
                file_count_check.how_much_done()
            result_dataset = self.result_infodict #InfoDict 클래스 {파일명:[erb 텍스트 라인]}
        else:
            print("특정 데이터셋으로 작업합니다.")
            result_dataset = ERBFilter().indent_maker(target_metalines) # [erb 텍스트 라인]
        CommonSent.extract_finished()
        return result_dataset


# 디버그용
if __name__ == '__main__':
    pass
