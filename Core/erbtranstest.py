from System.xmlhandling import ERBGrammarXML
from Ctrltool import CSVFunc
from customdb import ERBMetaInfo, InfoDict
from usefile import FileFilter, LoadFile, MakeLog, MenuPreset

class ERBWrite(LoadFile):
    def __init__(self,NameDir,EncodeType,era_type):
        super().__init__(NameDir,EncodeType)
        self.era_type = era_type
        self.chara_num = input("캐릭터의 번호를 입력해주세요. : ")
        # self.chara_num = chara_num
        self.set_xml = ERBGrammarXML('EraSetting.xml')
        self.gram_xml = ERBGrammarXML('CustomMarkdown.xml')
        with self.readonly() as txt_origin:
            self.txt_bulklines = txt_origin.readlines()

    def __make_dict(self,option_num):
        # 사전 데이터 준비작업. 추후 __init__이나 최초 1회 실행 구문으로 이관 필요 있음.
        self.csvvar_dict = CSVFunc().make_csv_var_dict() #TODO 임시 {csvvar:[csvname,num]}
        self.temp_dict = self.set_xml.check_templet(self.era_type)
        if option_num == 0: self.zname_dict = self.gram_xml.znames_dict()
        elif option_num == 1:
            print("ZNAME.erb 관련 변수를 사용하지 않습니다.")
            self.zname_dict = self.gram_xml.znames_dict(option_num=3)
        self.namedict_situ = self.gram_xml.zname_dict_situ()
        self.var_dict = self.gram_xml.vars_dict()

    def __replace_command(self,line):
        # '커맨드' 용 함수
        command = self.temp_dict['command'].replace('*',self.chara_num)
        command_with_num = command + line.split()[1]
        return command_with_num

    def __replace_situation(self,line):
        # '상황' 용 함수. IF문을 관리
        splited_line = line.split()
        for word in splited_line:
            if word in self.namedict_situ:
                line = line.replace(word,self.namedict_situ[word])
            elif word in self.var_dict:
                line = line.replace(word,self.var_dict[word])
        return 'IF '+line

    def __replace_branch(self,line):
        # '분기' 용 함수. CASE문이나 DATALIST문 관리
        pass

    def txt_to_metalines(self,option_num=0):
        #TODO 구상 번역기 총괄
        #TODO 스위치구문 등 활용해 커맨드별, IF문별, CASE문별 블럭 형성 가능하게
        self.__make_dict(option_num)
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
                erb_translated_list.append(self.__replace_command(line))
            elif line == '\n':
                pass
            else:
                erb_translated_list.append('PRINTFORMW '+line)
        if if_switch >= 1:
            for num in range(if_switch)-1:
                erb_translated_list.append('ENDIF\n')
        erb_metalines = ERBFilter().make_metainfo_lines(erb_translated_list,0,self.NameDir)
        return erb_metalines.linelist # list형 line

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
