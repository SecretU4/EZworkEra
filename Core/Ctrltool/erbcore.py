# ERB 관련 모듈
import re
from customdb import ERBMetaInfo, InfoDict
from usefile import FileFilter, LoadFile, LogPreset, MenuPreset
from util import CommonSent, DataFilter
from System.interface import StatusNum
from System.xmlhandling import ERBGrammarXML, SettingXML
from .erbblock import CheckStack
from . import CSVFunc

class ERBLoad(LoadFile):

    debug_log = LogPreset(2)

    def __init__(self,NameDir,EncodeType):
        super().__init__(NameDir,EncodeType)

    def make_erblines(self):
        return self.make_bulklines(self.debug_log)

    def search_line(self,*args,except_args=None):
        self.make_erblines()
        self.targeted_list = []
        skip_switch = 0
        for line in self.lines:
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


class ERBWrite(LoadFile):
    """자체 문법을 통한 ERB 작성 지원 클래스"""

    set_xml = SettingXML('EraSetting.xml')
    gram_xml = ERBGrammarXML('CustomMarkdown.xml')
    casetype_dict = {0:{'b_start':'SELECTCASE','c_start':'CASE','b_end':'ENDSELECT','c_end':None},
        1:{'b_start':'PRINTDATA','c_start':'DATALIST','b_end':'ENDDATA','c_end':'ENDLIST'}}

    def __init__(self,NameDir,EncodeType,era_type,chara_num):
        super().__init__(NameDir,EncodeType)
        self.era_type = era_type
        self.chara_num = chara_num
        self.debug_log = LogPreset(3)
        self.txt_bulklines = super().make_bulklines(self.debug_log)

    def __make_dict(self):
        # 사전 데이터 준비작업. 추후 __init__이나 최초 1회 실행 구문으로 이관 필요 있음.
        # csv 변수 양식에 맞게 불러줌. {csvvar:[csvname,num]}
        if self.csvvar_dict == None:
            self.csvvar_dict = CSVFunc().make_csv_var_dict()
        # Era 파생에 따라 다른 탬플릿을 불러옴.
        self.temp_dict = self.set_xml.check_templet(self.era_type)
        # 선택에 따라 다르지만, 호칭 관련 변수를 관리함. {class,name:{particle:{md:og}}}
        if self.zname_type == 0: self.gram_xml.znames_dict()
        elif self.zname_type == 1:
            print("ZNAME.erb 관련 변수를 사용하지 않습니다.")
            self.gram_xml.znames_dict(option_num=3)
        self.zname_dict = self.gram_xml.zname_comp_dict
        # {호칭 class:호칭 origin} ex: {당신:MASTER}
        self.namedict_situ = self.gram_xml.zname_dict_situ()
        # {class:{type:{md:og}}}}
        if_dict = {}
        for dic in self.gram_xml.vars_dict()['IF'].values():
            if_dict.update(dic)
        self.var_dict = if_dict
        self.user_dict = self.gram_xml.user_dict()

    def __handle_csvvar(self,word,last_word):
        dup_datalist = []
        dup_switch = 0
        now_switch = 0
        if '<지금>' in word:
            word.replace('<지금>','')
            now_switch = 1
        if self.csvvar_dict.get('dup1_'+word):
            self.__csvvar_dup_count += 1
            dup_switch = 1
            target_list = list(self.csvvar_dict.keys())
        else: target_list = [word]
        for var in target_list:
            if (var.endswith(word) and var.startswith('dup')) or word == var:
                csvvar_data = self.csvvar_dict[var]
                csv_name = FileFilter().sep_filename(csvvar_data[0]).upper()
                if now_switch:
                    if csv_name == 'EX': csv_name = 'NOWEX'
                if self.csvvar_type == 0:
                    word_withcsv = csv_name + ':' + word.replace('__',' ')
                elif self.csvvar_type == 1:
                    word_withcsv = '{}:{}'.format(csv_name,csvvar_data[1])
                dup_datalist.append(word_withcsv)
        if dup_switch:
            result = '!중복변수! 변수명={} {}'.format(word,' OR '.join(dup_datalist))
        else:
            result = word_withcsv
        if last_word in self.namedict_situ.values():
            result = result.replace(':',':{}:'.format(last_word))
            self.__namedict_used_switch = 1
        return result

    def handle_line(self,splited_line,*dicts):
        """분리된 문자열 리스트 받아 처리 후 문자열 리스트 return함."""
        re_splited_line = []
        self.__namedict_used_switch = 0
        last_word = None
        for word in splited_line:
            if word in self.namedict_situ: word = self.namedict_situ[word]
            elif word in self.var_dict: word = self.var_dict[word]
            elif word in self.csvvar_dict:
                word = self.__handle_csvvar(word,last_word)
            else:
                for dic in dicts:
                    if isinstance(dic,dict) and word in dic: word = dic[word]
            if self.__namedict_used_switch != 0:
                re_splited_line.pop()
                self.__namedict_used_switch = 0
            re_splited_line.append(word)
            last_word = word
        if re_splited_line == []: re_splited_line.append('')
        return re_splited_line

    def __replace_command(self,line):
        # '커맨드' 용 함수
        #TODO Era 파생마다 다른 양식에 적합하게 수정 필요. EraSetting.xml에 템플릿 만들어둠.
        command = self.temp_dict['command'].replace('*',self.chara_num)
        command_with_num = command + '_' + line.split()[1]
        self.erb_translated_list.append(command_with_num)

    def __replace_situation(self,line,before_if_level):
        # '상황' 용 함수. IF문을 관리
        splited_line = line.split()
        sit_head = splited_line.pop(0).replace('상황:','')
        if sit_head == '': self.__if_lv = 1
        else:
            try:
                self.__if_lv = self.__if_lv_list.index(sit_head) + 1
            except ValueError:
                self.__if_lv_list.append(sit_head)
                self.__if_lv = len(self.__if_lv_list)
        re_splited_line = []
        if splited_line[0] in ['이외','기타']:
            re_splited_line.append('ELSE')
        else:
            re_splited_line.extend(self.handle_line(splited_line,self.user_dict))
            if before_if_level < self.__if_lv:
                re_splited_line.insert(0,'IF')
            else:
                re_splited_line.insert(0,'ELSEIF')
        replaced_line = ' '.join(re_splited_line)
        self.erb_translated_list.append(replaced_line)

    def __replace_branch(self,line):
        # '분기' 용 함수. CASE문이나 DATALIST문 관리
        # 0: CASE 1: DATALIST
        splited_line = line.split()
        b_head = splited_line.pop(0).replace('분기:','')
        case_start = self.casetype_dict[self.casetype_mod]['c_start']
        if b_head == '': self.__cs_lv = 1
        elif b_head == '끝':
            self.__cs_lv -= 1
            self.__case_randswitch = 0
            self.erb_translated_list.append(line)
            return 0
        else:
            try:
                self.__cs_lv = self.__cs_lv_list.index(b_head) + 1
            except ValueError:
                self.__cs_lv_list.append(b_head)
                self.__cs_lv = len(self.__cs_lv_list)
        if self.casetype_mod == 0: # CASE
            re_splited_line = self.handle_line(splited_line,self.user_dict)
            if self.__cs_count == 0:
                if re_splited_line[0] in ['랜덤','RAND','RANDOM']:
                    start_case_line = 'RAND:'
                    self.__case_randswitch = 1
                else:
                    case_line = re_splited_line.pop()
                    start_case_line = ' '.join(re_splited_line)
                    re_splited_line = [case_line]
                self.__addline_loc[self.__line_count] = 'BRANCH_START ' + start_case_line
            if self.__case_randswitch == 1:
                case_start = '{} {}'.format(case_start,self.__cs_count)
            elif re_splited_line[0] in ['이외','기타']:
                case_start = case_start + 'ELSE'
                self.__cs_lv -= 1
            else:
                case_start = case_start + ' ' + ' '.join(re_splited_line)
        elif self.casetype_mod == 1: # DATALIST
            if self.__cs_count == 0:
                self.__addline_loc[self.__line_count] = 'BRANCH_START'
            else:
                self.__addline_loc[self.__line_count] = 'CASE_END'
        self.__cs_count += 1
        self.erb_translated_list.append(case_start + '\n')

    def __replace_print(self,line):
        raw_switch = 0
        splited_line = line.split()
        re_splited_line = []
        header_word = splited_line[0]
        if header_word == '=POZ=':
            splited_line.pop(0)
            head_word = 'PRINTFORML '
        elif header_word == '=RAW=':
            splited_line.pop(0)
            head_word = 'PRINTFORM '
            raw_switch = 1
        else:
            head_word = 'PRINTFORMW '
        for word in splited_line:
            if raw_switch == 1:
                re_splited_line = splited_line
                break
            word_search = word.split('>')[0]+'>'
            if word.startswith(';'): break
            elif self.zname_dict.get(word_search):
                word = word.replace(word_search,self.zname_dict[word_search])
            re_splited_line.append(word)
        if re_splited_line == []: re_splited_line.append('')
        return head_word+' '.join(re_splited_line)

    def __check_addline(self,before_if_level,before_case_level):
        # ENDIF,ENDSELECT 유무 판별
        if before_if_level > self.__if_lv:
            self.__addline_loc[self.__line_count] = 'ENDIF'
        elif before_case_level > self.__cs_lv:
            self.__addline_loc[self.__line_count] = 'BRANCH_END {}'.format(self.__cs_count)
            self.__cs_count = 0
        elif before_case_level < self.__cs_lv:
            pass
        if len(self.txt_bulklines) == self.__line_count + 1: # 모든 줄 변환 완료시
            branch_start = self.casetype_dict[self.casetype_mod]['b_start']
            branch_end = self.casetype_dict[self.casetype_mod]['b_end'] + '\n'
            case_end = str(self.casetype_dict[self.casetype_mod]['c_end']) + '\n'
            b_lv = 0
            loc_count = 0
            self.__addline_loclist = list(self.__addline_loc.keys())
            self.__addline_loclist.sort()
            self.__addline_loclist.reverse()
            for loc in self.__addline_loclist:
                if self.__addline_loc[loc] == 'ENDIF':
                    self.erb_translated_list.insert(loc,'ENDIF\n')
                    loc_count += 1
                elif 'CASE_END' in self.__addline_loc[loc]:
                    self.erb_translated_list.insert(loc,case_end)
                    loc_count += 1
                elif 'BRANCH_END' in self.__addline_loc[loc]:
                    self.erb_translated_list[loc] = branch_end
                    if self.casetype_mod == 0:
                        c_count = self.__addline_loc[loc].split()[-1]
                        self.__case_randswitch = 0
                    elif self.casetype_mod == 1:
                        self.erb_translated_list.insert(loc,case_end)
                    b_lv += 1
                elif 'BRANCH_START' in self.__addline_loc[loc]:
                    if 'BRANCH_START RAND:' == self.__addline_loc[loc]:
                        self.erb_translated_list.insert(loc,'{} RAND:{}'.format(branch_start,c_count))
                        c_count = 0
                    else:
                        if self.casetype_mod == 0:
                            orig_line = self.__addline_loc[loc].replace('BRANCH_START',branch_start)
                            self.erb_translated_list.insert(loc,orig_line)
                        elif self.casetype_mod == 1:
                            self.erb_translated_list.insert(loc,branch_start+'\n')
                            loc_count += 1
                    b_lv -= 1
                    loc_count = 0
            while self.__if_lv > 0:
                self.erb_translated_list.append('ENDIF\n')
                self.__if_lv -= 1
            if b_lv != 0:
                print("분기문 관리에 이상 있음.")

    def txt_to_erblines(self,csvvar_dict,zname_type=0,csvvar_type=0,casetype_mod=0):
        # 구상 번역기 총괄
        self.csvvar_dict = csvvar_dict
        self.zname_type = zname_type
        self.csvvar_type = csvvar_type # 0: 단어형 1: 숫자형
        self.casetype_mod = casetype_mod # 0: CASE 1: DATALIST
        self.__csvvar_dup_count = 0
        self.__make_dict()
        self.erb_translated_list = []
        self.__if_lv_list = [] # if 단계 구별자
        self.__cs_lv_list = []
        self.__addline_loc = {}
        self.__case_randswitch = 0
        self.__if_lv = 0
        self.__cs_lv = 0
        self.__cs_count = 0
        for index_line in enumerate(self.txt_bulklines):
            before_if_level = self.__if_lv
            before_case_level = self.__cs_lv
            self.__line_count, line = index_line
            line = line.strip()
            if line.startswith(';'):
                self.erb_translated_list.append(line)
            elif line.startswith('상황:'):
                self.__replace_situation(line,before_if_level)
            elif line.startswith('커맨드:'):
                self.__replace_command(line)
            elif line.startswith('분기:'):
                self.__replace_branch(line)
            elif self.casetype_mod == 1 and self.__cs_lv != 0:
                self.erb_translated_list.append('DATAFORM '+self.__replace_print(line))
            else:
                if line.startswith('===') or line.startswith('---'):
                    self.erb_translated_list.append('DRAWLINE\n')
                else:
                    self.erb_translated_list.append(self.__replace_print(line))
            self.__check_addline(before_if_level,before_case_level)

        if self.__csvvar_dup_count != 0:
            print("중의적인 csv변수가 발견되었습니다. '!중복변수!'를 결과물에서 검색하세요.")
        self.erb_translated_list.insert(0,';{}에서 가져옴\n'.format(self.NameDir))
        self.debug_log.end_log()
        return self.erb_translated_list


class ERBRemodel(ERBLoad):
    """이미 존재하는 ERB 파일의 내용 수정을 위한 클래스"""
    def __init__(self,NameDir,EncodeType,csv_infodict):
        super().__init__(NameDir,EncodeType)
        self.csvtrans_infodict = csv_infodict
        self.make_erblines()

    def replace_csvvars(self,mod_num=0):
        vfinder = ERBVFinder(self.csvtrans_infodict)
        replaced_context_list = []
        for index_line in enumerate(self.lines):
            line_count, line = index_line
            change_check = 0
            line = line.strip()
            if not line.startswith(';'):
                find_list = vfinder.find_csvfnc_line(line)
                if find_list:
                    rep_list = vfinder.change_var_index(find_list,mod_num)
                    orig_fncs = vfinder.print_csvfnc(rep_list)
                    comp_fncs = vfinder.print_csvfnc(rep_list,3)
                    for no in range(len(orig_fncs)):
                        orig_fnc = orig_fncs[no]
                        comp_fnc = comp_fncs[no]
                        if orig_fnc != comp_fnc:
                            line = line.replace(orig_fnc,comp_fnc)
                            change_check = 1
            replaced_context_list.append(line)
            if change_check: self.debug_log.write_log(str(line_count+1)+'행 index 변수 변환됨\n')

        self.debug_log.end_log('index 변수변환')
        return replaced_context_list


class ERBUtil:
    def indent_maker(self,target_metalines): # metaline을 들여쓰기된 lines로 만듦
        self.filtered_lines = []
        for line in target_metalines:
                if_level, case_level, _, context = line
                if context.startswith(';'): filtered_line = context
                else: filtered_line = '{}{}{}'.format('\t'*if_level,'\t'*case_level,context)
                if context.endswith('\n') != True: filtered_line = filtered_line + '\n'
                self.filtered_lines.append(filtered_line)
        if self.filtered_lines == []:
            print("결과물이 없습니다.")
            return None
        return self.filtered_lines

    def make_metainfo_lines(self,bulk_lines,option_num=0,target_name=None): # 0: 전부 1: 기능관련만
        self.command_count = 0
        skip_start = 0
        erb_info = ERBMetaInfo()
        erb_log = LogPreset(2)
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
                        erb_info.add_line_list(line)
                        erb_info.case_level += 1
                    elif line.startswith('CASE') == True:
                        erb_info.case_count += 1
                        if option_num == 1: continue
                        if erb_info.case_count != 1: erb_info.case_level -= 1
                        erb_info.add_line_list(line)
                        erb_info.case_level += 1
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
                        erb_info.case_level -= 1
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
        erb_log.sucessful_done()
        return erb_info

    def csv_infodict_maker(self,mod_num=0,debug_log=None):
        """infodict을 필요로하는 함수나 클래스에 사용함. debug_log은 LogPreset 타입을 요구함."""
        infodict_csv = MenuPreset().load_saved_data(0,"{}\n{}".format(
            "CSV 변수 목록 추출 데이터를 불러오실 수 있습니다.",
            "불러오실 경우 선택하신 모드와 다르게 작동할 수 있습니다."))
        if not infodict_csv:
            if mod_num in (0,1): # {csv파일명:{숫자:csv변수명}}
                infodict_csv = CSVFunc().import_all_CSV(1)
            elif mod_num == 2: # {csv파일명:{csv변수명:숫자}}
                infodict_csv = CSVFunc().import_all_CSV(2)
            else:
                raise NotImplementedError(mod_num)

        if debug_log:
            if mod_num == 0:
                log_text = '작업을 위해 csv infodict 불러옴'
            elif mod_num in (1, 2): # log_text 추가작성하는 경우
                if mod_num == 1:
                    log_text = '숫자를 index 변수로 변환'
                else:
                    log_text = 'index 변수를 숫자로 변환'
                log_text = 'ERB 내부 {}\n'.format(log_text)
            debug_log.write_log(log_text)
        return infodict_csv


class ERBVFinder:
    """문장 대응 csv 변수 필터. csvdict은 infodict형의 csv정보를 요구하며,
    log_set은 LogPreset 을 요구함
    """

    except_dict = {'UP':'JUEL','DOWN':'JUEL','PARAM':'PALAM',
        'NOWEX':'EX','UPBASE':'BASE','DOWNBASE':'BASE'}
    symbol_filter = r':([^&=,;\*\#\$\%\/\|\!\+\-\.\(\)\<\>\{\}\r\n]+)'
    # target_list = ['TARGET','PLAYER','MASTER','ASSI'] #TODO 차원지원 필요함

    def __init__(self,csvdict,log_set=None):
        if isinstance(csvdict, InfoDict):
            self.csv_infodict = csvdict
            self.csv_fnames = dict()
            for filename in list(self.csv_infodict.dict_main.keys()):
                csvname = FileFilter().sep_filename(filename).upper()
                self.csv_fnames[csvname] = filename
            self.csv_head = list(self.csv_fnames.keys())
        elif isinstance(csvdict, list): self.csv_head = csvdict
        else: raise TypeError
        csv_all_head = self.csv_head + list(self.except_dict.keys())
        re_varshead = '({})'.format('|'.join(csv_all_head))
        self.csvvar_re = re.compile(re_varshead+self.symbol_filter)
        self.log_set = log_set

    def find_csvfnc_line(self,line):
        """해당하는 결과물이 있을 시 [(csv명,변수내용,ERB상 함수명,대명사)] 로 출력함.
        이외는 None 리턴"""
        if line.startswith(';'): return None
        line = line.split(';')[0]
        line_search = self.csvvar_re.findall(line) # [(var1,arg1),(var2,arg2)...]
        find_result = []
        for var_bulk in line_search:
            var_head, var_context = var_bulk
            var_head = var_head.strip()
            var_context = var_context.strip()
            if ':' in var_context:
                var_pnoun, var_context_t, *etc= var_context.split(':')
                if etc:
                    print(var_bulk,"개발자에게 보고바람")
            else:
                var_pnoun = None
                var_context_t = var_context
            if self.except_dict.get(var_head): var_head_t = self.except_dict[var_head]
            else: var_head_t = var_head
            find_result.append((var_head_t,var_context_t,var_head,var_pnoun))
        if find_result: return find_result
        else: return None

    def change_var_index(self,found_result,mod_num=0):
        """find_csvfnc_line의 결과값을 받아 context을 변환한 후 다시 리스트 리턴.

        mod_num 0 : 숫자 > 단어, mod_num 1 : 단어 > 숫자
        """
        index_count = 0
        if self.csv_infodict.db_ver > 1.2:
            reversed_dict = self.csv_infodict.make_reverse()
        else:
            reversed_dict = None
        for result in found_result:
            if result:
                var_head, var_context, orig_head, p_noun = result
                int_checker = list(filter(str.isdecimal,var_context))
                if (mod_num == 0 and int_checker) or (
                    mod_num == 1 and int_checker != list(var_context)):
                    try:
                        csv_filename = self.csv_fnames[var_head]
                        context_t = self.csv_infodict.dict_main[csv_filename].get(var_context)
                        if not context_t and reversed_dict:
                            context_t = reversed_dict[csv_filename].get(var_context)
                        found_result[index_count] = (var_head, (
                            var_context, context_t), orig_head, p_noun)
                    except KeyError:
                        if self.log_set:
                            self.log_set.write_error_log(KeyError,orig_head)
            index_count += 1
        return found_result

    def print_csvfnc(self,comp_list,opt_no=0):
        """line에서 추출된 erb내 변수 리스트를 다시 결합한 목록 리턴

        opt_no
            0: 디폴트. erb 내 원래 형태로 출력
            1: csv에서 인식되는 형태로 출력 (대명사 포함)
            2: csv에서 인식되는 형태로 출력 (대명사 제외)
            3: (index 변환 사용시) erb 내 index 변환 행태로 출력
        """
        result_list = []
        if not comp_list: return None
        for fncinfo in comp_list:
            csvhead, context, orighead, pnoun = fncinfo
            if isinstance(context,tuple):
                o_context, t_context = context
                if not t_context:
                    t_context = o_context
                    if self.log_set:
                        self.log_set.write_log("{} index not found in {}".format(o_context,csvhead))
            elif isinstance(context,str): o_context = t_context = context
            else: raise TypeError
            if opt_no == 0:
                head, cont = orighead, o_context
            elif opt_no in (1, 2):
                head, cont = csvhead, o_context
            elif opt_no == 3:
                head, cont = orighead, t_context
            if pnoun and opt_no in (0, 1, 3):
                cont = pnoun + ':' + cont
            result_list.append('{}:{}'.format(head,cont))
        return result_list


class ERBBlkFinder:
    """디렉토리 대응 코드 블럭 인식 클래스"""
    def __init__(self):
        self.block_data = InfoDict(1) # {filename:{index:(func,(code_block))}}
        self.files, self.encode_type = FileFilter(1).get_filelist('ERB')

    def block_maker(self):
        for filename in self.files:
            opened_erbs = ERBLoad(filename,self.encode_type)
            chk_stk = CheckStack(opened_erbs.make_erblines()).line_divider()
            self.block_data.add_dict(filename,chk_stk)
        return self.block_data

    def block_checker(self):
        #TODO 파일별/ 블럭별 분리 및 공통점(구문 위치) 확인해 변경사항 체크
        pass

    def block_showdiff(self):
        while not isinstance(self.block_data,InfoDict):
            self.block_data = MenuPreset().load_saved_data()
            if self.block_data is None:
                print('특정 디렉토리의 ERB 데이터를 불러옵니다.')
                self.block_maker()


class ERBFunc:

    func_log = LogPreset('ERBwork')

    def __init__(self):
        self.result_infodict = InfoDict(1)

    def extract_printfunc(self,erb_files=None,encode_type=None):
        print("PRINT/DATAFORM 구문의 추출을 시작합니다.")
        if not erb_files or not encode_type:
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
        self.func_log.sucessful_done()
        return self.result_infodict # {파일명:lines} 형태가 포함된 infodict

    def search_csv_var(self,erb_files=None,encode_type=None):
        print("ERB 파일에서 사용된 CSV 변수목록을 추출합니다.")
        if not erb_files or not encode_type:
            erb_files, encode_type = FileFilter().get_filelist('ERB')
        csvvar_list = ERBUtil().csv_infodict_maker()
        if csvvar_list == None:
            csvvar_list = CSVFunc().single_csv_read('CSVfnclist.csv',opt=2)
        vfinder = ERBVFinder(csvvar_list)
        file_count_check = StatusNum(erb_files,'파일')
        file_count_check.how_much_there()

        for filename in erb_files:
            erb_bulk = ERBLoad(filename, encode_type).make_erblines()
            self.func_log.write_loaded_log(filename)
            file_results = []
            for line in erb_bulk:
                vars_list = vfinder.find_csvfnc_line(line)
                if vars_list: file_results.extend(vars_list)
            dup_res_list = DataFilter().dup_filter(file_results)
            var_check = dict()
            for fnc_info in dup_res_list:
                fnchead, fnctext, _, _ = fnc_info
                if fnchead not in var_check.keys(): var_check[fnchead] = list()
                var_check[fnchead].append(fnctext)
            result_lines = ['파일명: {}에서 이하의 변수가 발견됨.\n\n'.format(filename)]
            for varkey in var_check.keys():
                context_list = DataFilter().dup_filter(var_check[varkey])
                result_lines.append(varkey + '를 참조함\n')
                result_lines.append(', '.join(context_list))
                result_lines.append('\n\n')
            self.result_infodict.add_dict(filename,result_lines)
            file_count_check.how_much_done()

        CommonSent.extract_finished()
        self.func_log.sucessful_done()
        return self.result_infodict # {파일명:정보 텍스트} 형태의 infodict

    def remodel_indent(self,metainfo_option_num=None,target_metalines=None):
        if target_metalines == None:
            print("들여쓰기를 자동 교정하는 유틸리티입니다.")
            erb_files, encode_type = FileFilter().get_filelist('ERB')
            file_count_check = StatusNum(erb_files,'파일')
            file_count_check.how_much_there()

            for filename in erb_files:
                erb_bulk = ERBLoad(filename,encode_type).make_erblines()
                lines = ERBUtil.make_metainfo_lines(
                    erb_bulk,metainfo_option_num,filename).linelist
                lines.insert(0,[0,0,0,";{}에서 불러옴\n".format(filename)])
                self.result_infodict.add_dict(filename,ERBUtil().indent_maker(lines))
                file_count_check.how_much_done()

            result_dataset = self.result_infodict #InfoDict 클래스 {파일명:[erb 텍스트 라인]}
        else:
            result_dataset = ERBUtil().indent_maker(target_metalines) # [erb 텍스트 라인]
        CommonSent.extract_finished()
        self.func_log.sucessful_done()
        return result_dataset

    def translate_txt_to_erb(self,era_type,csvvar_dict):
        txt_files,encode_type = FileFilter().get_filelist('TXT')
        file_count_check = StatusNum(txt_files,'파일')
        file_count_check.how_much_there()
        chara_num = input("작성하실 캐릭터의 번호를 입력해주세요. : ")
        self.comp_lines = []

        for filename in txt_files:
           file_lines = ERBWrite(filename,encode_type,era_type,chara_num).txt_to_erblines(csvvar_dict)
           print("{}의 처리가 완료되었습니다.".format(filename))
           self.comp_lines.extend(file_lines)
           file_count_check.how_much_done()

        erb_metainfo = ERBUtil().make_metainfo_lines(self.comp_lines,0,filename)
        self.func_log.sucessful_done()
        return erb_metainfo

    def replace_num_or_name(self,mod_num=0,erb_files=None,encode_type=None):
        """0:숫자 > 변수, 1: 변수 > 숫자"""
        if not erb_files or not encode_type:
            erb_files, encode_type = FileFilter().get_filelist('ERB')
        file_count_check = StatusNum(erb_files,'ERB 파일')
        file_count_check.how_much_there()
        csv_infodict = ERBUtil().csv_infodict_maker(mod_num+1,self.func_log)
        print("ERB내 index 변환작업을 시작합니다.")

        for filename in erb_files:
            replaced_lines = ERBRemodel(filename,encode_type,csv_infodict).replace_csvvars(mod_num)
            self.result_infodict.add_dict(filename,replaced_lines)
            file_count_check.how_much_done()

        CommonSent.extract_finished()
        self.func_log.sucessful_done()
        return self.result_infodict # {파일명:[바뀐줄]}

    def erb_trans_helper(self): #TODO 공사중
        """번역본의 원본 이식에 도움을 주는 함수"""
        print("원본 erb의 디렉토리를 지정해주세요.")
        o_blkdata = ERBBlkFinder()
        print("번역본 erb의 디렉토리를 지정해주세요.")
        t_blkdata = ERBBlkFinder()
        #TODO 이름만 다른 파일 비교 가능하게 - CompareErb.csv 활용
