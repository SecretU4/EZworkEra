# ERB 관련 모듈
from customdb import ERBMetaInfo, InfoDict
from usefile import FileFilter, LoadFile, MakeLog, MenuPreset
from util import CommonSent, DataFilter
from System.interface import StatusNum
from System.xmlhandling import ERBGrammarXML
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

#TODO ERB 구상 번역기 공사중.
'''class ERBWrite(LoadFile):
    def __init__(self,NameDir,EncodeType):
        super().__init__(NameDir,EncodeType)
        self.set_xml = ERBGrammarXML('EraSetting.xml')
        self.gram_xml = ERBGrammarXML('CustomMarkdown.xml')
        with self.readonly() as txt_origin:
            self.txt_bulklines = txt_origin.readlines()

    def __replace_csvvar(self):
        csv_dict = CSVFunc().make_csv_var_dict() #TODO 임시 {csvvar:[csvname,num]}

    def __replace_command(self,line,era_type,chara_num):
        temp_dict = self.set_xml.check_templet(era_type)
        command = temp_dict['command'].replace('*',chara_num)
        command_with_num = command + line.split()[1]
        return command_with_num

    def __replace_situation(self,line):
        csvvar_dict = self.__replace_csvvar()
        namedict_situ = self.gram_xml.zname_dict_situ()
        var_dict = self.gram_xml.vars_dict()
        splited_line = line.split()
        for word in splited_line:
            if word in namedict_situ:
                line = line.replace(word,namedict_situ[word])
            elif word in var_dict:
                line = line.replace(word,var_dict[word])
        return 'IF '+line

    def __replace_branch(self,line):
        pass

    def txt_to_metalines(self,era_type,option_num=0): #TODO 구상 번역기
        if option_num == 0: zname_dict = self.gram_xml.znames_dict()
        elif option_num == 1:
            print("ZNAME.erb 관련 변수를 사용하지 않습니다.")
            zname_dict = self.gram_xml.znames_dict(option_num=3)
        erb_translated_list = []
        command_switch = 0
        if_switch = 0
        for line in self.txt_bulklines:
            if line.startswith('상황:'):
                erb_translated_list.append(self.__replace_situation(line))
            #TODO {'var':{class:{type:{md:og}}}
            elif line.startswith('분기:'):
                erb_translated_list.append(self.__replace_branch(line))
            elif line.startswith('커맨드:'):
                chara_num = input("캐릭터의 번호를 입력해주세요. : ")
                erb_translated_list.append(self.__replace_command(line,era_type,chara_num))
            elif line == '\n':
                pass
            else:
                erb_translated_list.append('PRINTFORMW '+line)
        if if_switch >= 1:
            for num in range(if_switch)-1:
                erb_translated_list.append('ENDIF\n')
        erb_metalines = ERBFilter().make_metainfo_lines(erb_translated_list,0,self.NameDir)
        return erb_metalines.linelist # list형 line

    def import_erbtext_info(self,situation,context,cases):
        pass
'''

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
