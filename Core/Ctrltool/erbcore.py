# ERB 관련 모듈
import re
from customdb import ERBMetaInfo, InfoDict, SheetInfo
from usefile import CustomInput, FileFilter, LoadFile, LogPreset, MenuPreset
from util import CommonSent, DataFilter
from System.interface import StatusNum
from System.xmlhandling import ERBGrammarXML, SettingXML
from .erbblock import CheckStack
from . import CSVFunc


class ERBLoad(LoadFile):

    debug_log = LogPreset(2)

    def __init__(self, NameDir, EncodeType):
        super().__init__(NameDir, EncodeType)

    def make_erblines(self):
        return self.make_bulklines(self.debug_log)

    def search_line(self, *args, except_args=None, opt=0):
        """불러온 ERB 파일 내 특정 단어가 포함된 행 리스트 출력
        
        opt bit 1 : 참이면 startswith인 경우에만 결과에 포함
        """
        self.make_erblines()
        targeted_list = []
        skip_switch = 0
        for line in self.lines:
            if skip_switch == 1:
                if "[SKIPEND]" in line:
                    skip_switch = 0
                continue
            else:
                if "[SKIPSTART]" in line:
                    skip_switch = 1
                    continue
                elif except_args != None:
                    for except_arg in except_args:
                        if except_arg in line:
                            continue
                for target in args:
                    if target in line:
                        if opt & 0b1 and not line.strip().startswith(target):
                            continue
                        targeted_list.append(line)
                        break
        return targeted_list


class ERBWrite(LoadFile):
    """자체 문법을 통한 ERB 작성 지원 클래스"""

    casetype_dict = {
        0: {"b_start": "SELECTCASE", "c_start": "CASE", "b_end": "ENDSELECT", "c_end": None},
        1: {"b_start": "PRINTDATA", "c_start": "DATALIST", "b_end": "ENDDATA", "c_end": "ENDLIST"},
    }

    def __init__(self, NameDir, EncodeType, era_type, chara_num):
        super().__init__(NameDir, EncodeType)
        self.era_type = era_type
        self.chara_num = chara_num
        self.debug_log = LogPreset(3)
        self.txt_bulklines = super().make_bulklines(self.debug_log)

    def __make_dict(self):
        self.set_xml = SettingXML("EraSetting.xml")
        self.gram_xml = ERBGrammarXML("CustomMarkdown.xml")
        # 사전 데이터 준비작업. 추후 __init__이나 최초 1회 실행 구문으로 이관 필요 있음.
        # csv 변수 양식에 맞게 불러줌. {csvvar:[csvname,num]}
        if self.csvvar_dict == None:
            self.csvvar_dict = CSVFunc().make_csv_var_dict()
        # Era 파생에 따라 다른 탬플릿을 불러옴.
        self.temp_dict = self.set_xml.check_templet(self.era_type)
        # 선택에 따라 다르지만, 호칭 관련 변수를 관리함. {class,name:{particle:{md:og}}}
        if self.zname_type == 0:
            self.gram_xml.znames_dict()
        elif self.zname_type == 1:
            print("ZNAME.erb 관련 변수를 사용하지 않습니다.")
            self.gram_xml.znames_dict(option_num=3)
        self.zname_dict = self.gram_xml.zname_comp_dict
        # {호칭 class:호칭 origin} ex: {당신:MASTER}
        self.namedict_situ = self.gram_xml.zname_dict_situ()
        # {class:{type:{md:og}}}}
        if_dict = {}
        for dic in self.gram_xml.vars_dict()["IF"].values():
            if_dict.update(dic)
        self.var_dict = if_dict
        self.user_dict = self.gram_xml.user_dict()

    def __handle_csvvar(self, word, last_word):
        dup_datalist = []
        dup_switch = 0
        now_switch = 0
        if "<지금>" in word:
            word.replace("<지금>", "")
            now_switch = 1
        if self.csvvar_dict.get("dup1_" + word):
            self.__csvvar_dup_count += 1
            dup_switch = 1
            target_list = list(self.csvvar_dict.keys())
        else:
            target_list = [word]
        for var in target_list:
            if (var.endswith(word) and var.startswith("dup")) or word == var:
                csvvar_data = self.csvvar_dict[var]
                csv_name = FileFilter().sep_filename(csvvar_data[0]).upper()
                if now_switch:
                    if csv_name == "EX":
                        csv_name = "NOWEX"
                if self.csvvar_type == 0:
                    word_withcsv = csv_name + ":" + word.replace("__", " ")
                elif self.csvvar_type == 1:
                    word_withcsv = "{}:{}".format(csv_name, csvvar_data[1])
                dup_datalist.append(word_withcsv)
        if dup_switch:
            result = "!중복변수! 변수명={} {}".format(word, " OR ".join(dup_datalist))
        else:
            result = word_withcsv
        if last_word in self.namedict_situ.values():
            result = result.replace(":", ":{}:".format(last_word))
            self.__namedict_used_switch = 1
        return result

    def handle_line(self, splited_line, *dicts):
        """분리된 문자열 리스트 받아 처리 후 문자열 리스트 return함."""
        re_splited_line = []
        self.__namedict_used_switch = 0
        last_word = None
        for word in splited_line:
            if word in self.namedict_situ:
                word = self.namedict_situ[word]
            elif word in self.var_dict:
                word = self.var_dict[word]
            elif word in self.csvvar_dict:
                word = self.__handle_csvvar(word, last_word)
            else:
                for dic in dicts:
                    if isinstance(dic, dict) and word in dic:
                        word = dic[word]
            if self.__namedict_used_switch != 0:
                re_splited_line.pop()
                self.__namedict_used_switch = 0
            re_splited_line.append(word)
            last_word = word
        if re_splited_line == []:
            re_splited_line.append("")
        return re_splited_line

    def __replace_command(self, line):
        # '커맨드' 용 함수
        # TODO Era 파생마다 다른 양식에 적합하게 수정 필요. EraSetting.xml에 템플릿 만들어둠.
        command = self.temp_dict["command"].replace("*", self.chara_num)
        command_with_num = command + "_" + line.split()[1]
        self.erb_translated_list.append(command_with_num)

    def __replace_situation(self, line, before_if_level):
        # '상황' 용 함수. IF문을 관리
        splited_line = line.split()
        sit_head = splited_line.pop(0).replace("상황:", "")
        if sit_head == "":
            self.__if_lv = 1
        else:
            try:
                self.__if_lv = self.__if_lv_list.index(sit_head) + 1
            except ValueError:
                self.__if_lv_list.append(sit_head)
                self.__if_lv = len(self.__if_lv_list)
        re_splited_line = []
        if splited_line[0] in ["이외", "기타"]:
            re_splited_line.append("ELSE")
        else:
            re_splited_line.extend(self.handle_line(splited_line, self.user_dict))
            if before_if_level < self.__if_lv:
                re_splited_line.insert(0, "IF")
            else:
                re_splited_line.insert(0, "ELSEIF")
        replaced_line = " ".join(re_splited_line)
        self.erb_translated_list.append(replaced_line)

    def __replace_branch(self, line):
        # '분기' 용 함수. CASE문이나 DATALIST문 관리
        # 0: CASE 1: DATALIST
        splited_line = line.split()
        b_head = splited_line.pop(0).replace("분기:", "")
        case_start = self.casetype_dict[self.casetype_mod]["c_start"]
        if b_head == "":
            self.__cs_lv = 1
        elif b_head == "끝":
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
        if self.casetype_mod == 0:  # CASE
            re_splited_line = self.handle_line(splited_line, self.user_dict)
            if self.__cs_count == 0:
                if re_splited_line[0] in ["랜덤", "RAND", "RANDOM"]:
                    start_case_line = "RAND:"
                    self.__case_randswitch = 1
                else:
                    case_line = re_splited_line.pop()
                    start_case_line = " ".join(re_splited_line)
                    re_splited_line = [case_line]
                self.__addline_loc[self.__line_count] = "BRANCH_START " + start_case_line
            if self.__case_randswitch == 1:
                case_start = "{} {}".format(case_start, self.__cs_count)
            elif re_splited_line[0] in ["이외", "기타"]:
                case_start = case_start + "ELSE"
                self.__cs_lv -= 1
            else:
                case_start = case_start + " " + " ".join(re_splited_line)
        elif self.casetype_mod == 1:  # DATALIST
            if self.__cs_count == 0:
                self.__addline_loc[self.__line_count] = "BRANCH_START"
            else:
                self.__addline_loc[self.__line_count] = "CASE_END"
        self.__cs_count += 1
        self.erb_translated_list.append(case_start + "\n")

    def __replace_print(self, line):
        raw_switch = 0
        splited_line = line.split()
        re_splited_line = []
        header_word = splited_line[0]
        if header_word == "=POZ=":
            splited_line.pop(0)
            head_word = "PRINTFORML "
        elif header_word == "=RAW=":
            splited_line.pop(0)
            head_word = "PRINTFORM "
            raw_switch = 1
        else:
            head_word = "PRINTFORMW "
        for word in splited_line:
            if raw_switch == 1:
                re_splited_line = splited_line
                break
            word_search = word.split(">")[0] + ">"
            if word.startswith(";"):
                break
            elif self.zname_dict.get(word_search):
                word = word.replace(word_search, self.zname_dict[word_search])
            re_splited_line.append(word)
        if re_splited_line == []:
            re_splited_line.append("")
        return head_word + " ".join(re_splited_line)

    def __check_addline(self, before_if_level, before_case_level):
        # ENDIF,ENDSELECT 유무 판별
        if before_if_level > self.__if_lv:
            self.__addline_loc[self.__line_count] = "ENDIF"
        elif before_case_level > self.__cs_lv:
            self.__addline_loc[self.__line_count] = "BRANCH_END {}".format(self.__cs_count)
            self.__cs_count = 0
        elif before_case_level < self.__cs_lv:
            pass
        if len(self.txt_bulklines) == self.__line_count + 1:  # 모든 줄 변환 완료시
            branch_start = self.casetype_dict[self.casetype_mod]["b_start"]
            branch_end = self.casetype_dict[self.casetype_mod]["b_end"] + "\n"
            case_end = str(self.casetype_dict[self.casetype_mod]["c_end"]) + "\n"
            b_lv = 0
            loc_count = 0
            self.__addline_loclist = list(self.__addline_loc.keys())
            self.__addline_loclist.sort()
            self.__addline_loclist.reverse()
            for loc in self.__addline_loclist:
                if self.__addline_loc[loc] == "ENDIF":
                    self.erb_translated_list.insert(loc, "ENDIF\n")
                    loc_count += 1
                elif "CASE_END" in self.__addline_loc[loc]:
                    self.erb_translated_list.insert(loc, case_end)
                    loc_count += 1
                elif "BRANCH_END" in self.__addline_loc[loc]:
                    self.erb_translated_list[loc] = branch_end
                    if self.casetype_mod == 0:
                        c_count = self.__addline_loc[loc].split()[-1]
                        self.__case_randswitch = 0
                    elif self.casetype_mod == 1:
                        self.erb_translated_list.insert(loc, case_end)
                    b_lv += 1
                elif "BRANCH_START" in self.__addline_loc[loc]:
                    if "BRANCH_START RAND:" == self.__addline_loc[loc]:
                        self.erb_translated_list.insert(
                            loc, "{} RAND:{}".format(branch_start, c_count)
                        )
                        c_count = 0
                    else:
                        if self.casetype_mod == 0:
                            orig_line = self.__addline_loc[loc].replace(
                                "BRANCH_START", branch_start
                            )
                            self.erb_translated_list.insert(loc, orig_line)
                        elif self.casetype_mod == 1:
                            self.erb_translated_list.insert(loc, branch_start + "\n")
                            loc_count += 1
                    b_lv -= 1
                    loc_count = 0
            while self.__if_lv > 0:
                self.erb_translated_list.append("ENDIF\n")
                self.__if_lv -= 1
            if b_lv != 0:
                print("분기문 관리에 이상 있음.")

    def txt_to_erblines(self, csvvar_dict, zname_type=0, csvvar_type=0, casetype_mod=0):
        # 구상 번역기 총괄
        self.csvvar_dict = csvvar_dict
        self.zname_type = zname_type
        self.csvvar_type = csvvar_type  # 0: 단어형 1: 숫자형
        self.casetype_mod = casetype_mod  # 0: CASE 1: DATALIST
        self.__csvvar_dup_count = 0
        self.__make_dict()
        self.erb_translated_list = []
        self.__if_lv_list = []  # if 단계 구별자
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
            if line.startswith(";"):
                self.erb_translated_list.append(line)
            elif line.startswith("상황:"):
                self.__replace_situation(line, before_if_level)
            elif line.startswith("커맨드:"):
                self.__replace_command(line)
            elif line.startswith("분기:"):
                self.__replace_branch(line)
            elif self.casetype_mod == 1 and self.__cs_lv != 0:
                self.erb_translated_list.append("DATAFORM " + self.__replace_print(line))
            else:
                if line.startswith("===") or line.startswith("---"):
                    self.erb_translated_list.append("DRAWLINE\n")
                else:
                    self.erb_translated_list.append(self.__replace_print(line))
            self.__check_addline(before_if_level, before_case_level)

        if self.__csvvar_dup_count != 0:
            print("중의적인 csv변수가 발견되었습니다. '!중복변수!'를 결과물에서 검색하세요.")
        self.erb_translated_list.insert(0, ";{}에서 가져옴\n".format(self.NameDir))
        self.debug_log.end_log()
        return self.erb_translated_list


class ERBRemodel:
    """이미 존재하는 ERB 파일의 내용 수정을 위한 클래스"""

    debug_log = LogPreset(2)

    def __init__(self, lines:list[str]):
        self.lines = lines

    express_dict = {
        "W":"\\t",
        "L":"\\n"
    }
    save_str_var = "LOCALS:85"
    re_single_sent = re.compile('@"(.+)"\n$')

    def replace_csvvars(self, csv_infodict, mod_num=0, srs_dict: dict = dict()):
        vfinder = ERBVFinder(csv_infodict)
        result_lines:list[str] = []
        for line_count, line in enumerate(self.lines):
            change_check = False
            line = line.strip()
            if not line.startswith(";"):
                find_list = vfinder.find_csvfnc_line(line)
                if find_list:
                    rep_list = vfinder.change_var_index(find_list, mod_num)
                    orig_fncs, comp_fncs = vfinder.print_csvfnc(rep_list, 0b1001)
                    for no in range(len(orig_fncs)):
                        orig_fnc = orig_fncs[no]
                        comp_fnc = comp_fncs[no]
                        if orig_fnc != comp_fnc:
                            o_context = rep_list[no][1][0]
                            if srs_dict.get(o_context):
                                line = line.replace(o_context, srs_dict[o_context])
                            else:
                                line = line.replace(orig_fnc, comp_fnc)
                            change_check = True
            result_lines.append(line + "\n")
            if change_check:
                self.debug_log.write_log(str(line_count + 1) + "행 index 변수 변환됨\n")

        self.debug_log.end_log("index 변수변환")
        return result_lines

    def _check_print_line(self, line:str):
        """PRINT구문의 체크 함수"""
        print_pat = re.compile("PRINT(V|S|FORM|FORMS|)(C|LC|)(K|D|)(L|W|)")
        pat_result = print_pat.match(line)
        if pat_result:
            print_head = pat_result.group()
            print_sp = pat_result.group(1)
            context = " ".join(line.split()[1:])
            endword = ""
            if print_head or print_sp:
                for key in self.express_dict:
                    if key in print_head:
                        endword = self.express_dict[key]
                        break
                if print_sp:
                    if "PRINTS" in print_head:
                        context = "%{0}%".format(context)
                    elif "PRINTV" in print_head:
                        context = "\{%s\}" % context
                    else:
                        raise NotImplementedError(print_head)
                
                return '@"%s%s" + \n' % (context, endword)
        return ""

    def __after_printcheck(self, target_lines:list[str], count:int):
        target_lines[-1] = target_lines[-1].replace(" + \n", "\n")
        if count == 1: # PRINT 출력문이 1줄짜리일 때
            for counting in range(1, count + 1):
                print_tail = ""
                temp_line = target_lines[-1 * counting]
                for item in self.express_dict.items():
                    if '%s" + \n' % item[-1] in temp_line: # <endword>" + \n
                        print_tail = item[0]
                        temp_line = temp_line.replace('%s" + \n' % item[-1], '"\n')
                    elif '%s"\n' % item[-1] in temp_line: # <endword>"\n
                        print_tail = item[0]
                        temp_line = temp_line.replace('%s"\n' % item[-1], '"\n')
                context = self.re_single_sent.match(temp_line).group(1)
                temp_line = "PRINTFORM%s %s\n" % (print_tail, context)
                target_lines[-1 * counting] = temp_line
            target_lines.pop(-(count + 1)) # "%s '=\n" % self.save_str_var
            target_lines.pop(-(count + 1)) # "{\n"
        else:
            target_lines.append("}\n")
            target_lines.append("CALL PRINTER, %s\n" % self.save_str_var)
        return target_lines

    def memory_optimize(self):
        result_lines = []
        count_print = 0
        for line in self.lines:
            result_line = self._check_print_line(line)
            if result_line:
                if not count_print:
                    result_lines.append("{\n")
                    result_lines.append("%s '=\n" % self.save_str_var)
                count_print += 1
            else:
                result_line = line
                if count_print:
                    result_lines = self.__after_printcheck(result_lines, count_print)

                count_print = 0
            result_line = result_line.replace("\r\n", "\n")
            result_lines.append(result_line)

        if '" + \n' in result_lines[-1]: # PRINT 출력문으로 파일이 끝날 때 처리
            result_lines = self.__after_printcheck(result_lines, count_print)

        return result_lines

    def replace_zname(self, lines:list[str], rem_flag=False, z_dict:dict = dict()):
        """zname 관련 변수 변환 함수
        rem_flag : True 이면 zname 추가, False면 zname 삭제
        z_dict는 #DEFINE 기반 zname.erh 딕셔너리 상정
        """
        rep_dict = {}
        pat_str = "(조사처리|조사만처리)\\(([\\S]+), (\"(\\D+)\"|'(\\D+)')\\)"
        if z_dict:
            pnoun_dict = {}
            zname_dict = {}
            for vname, val in z_dict:
                for match in re.compile(pat_str).finditer(val):
                    pnoun_dict[vname] = match.group(2)
                    zname_dict[match.group(4)] = ""
        else:
            pnoun_dict = {
                "ARG":"CALLNAME:ARG",
                "마스터":"CALLNAME:MASTER",
                "조교자":"CALLNAME:PLAYER",
                "타겟":"CALLNAME:TARGET",
                "조수":"CALLNAME:ASSI"
            }
            zname_dict = {
                "이며":"で", "며":"で", "이고":"も", "고":"も",
                "이라":"で", "라":"で", "이다":"だ", "다":"だ",
                "이였":"だっ", "였":"だっ", "이여":"で", "여":"で", 
                "이야":"は", "야":"は",  "이나":"", "나":"",
                "이면":"なら", "면":"なら",
                "은":"は", "는":"は", "이":"が", "가":"が",
                "을":"を", "를":"を", "과":"と", "와":"と",
                "으로":"に", "로":"に", "랑":"と", "이랑":"と",
                }

        for pnoun, pnoun_o in pnoun_dict.items():
            for zname, zname_o in zname_dict.items():
                key = "%{}{}%".format(pnoun, zname)
                rep_dict[key] = "%{}%{}".format(pnoun_o, zname_o)

        pat_search = "%([^%]+)%"
        if rem_flag: # zname 추가
            rep_dict = {val:key for key, val in rep_dict.items()}
            pat_search += "(\\D)"
        else: # zname 제거
            pat_zname = '|'.join(zname_dict.keys())
            re_zfunc = re.compile(
                "%{}%".format(pat_str).replace("\\D+", pat_zname)
                )
        result:list[str] = []
        for line in lines:
            if not rem_flag:
                zfunc_iter = re_zfunc.finditer(line)
                for zfunc in zfunc_iter: # 조사처리/조사처리만 함수 제거
                    exist_zfnc = zfunc.group()
                    orig_var = zfunc.group(2)
                    line = line.replace(exist_zfnc, "%{}%".format(orig_var))
            for strs in re.compile(pat_search).finditer(line):
                context = strs.group()
                rep_str = rep_dict.get(context)
                if rep_str:
                    line = line.replace(context, rep_str)
            result.append(line)

        return result


class ERBUtil:
    def indent_maker(self, metalineinfo):  # metaline을 들여쓰기된 lines로 만듦
        self.filtered_lines = []
        target_metalines = metalineinfo.linelist
        for line in target_metalines:
            if_level, case_level, _, context = line
            if context.startswith(";"):
                filtered_line = context
            else:
                filtered_line = "{}{}{}".format("\t" * if_level, "\t" * case_level, context)
            if context.endswith("\n") != True:
                filtered_line = filtered_line + "\n"
            self.filtered_lines.append(filtered_line)
        if self.filtered_lines == []:
            print("결과물이 없습니다.")
            return None
        return self.filtered_lines

    def make_metainfo_lines(self, bulk_lines, option_num=0, target_name=None):  # 0: 전부 1: 기능관련만
        skip_start = 0
        erb_info = ERBMetaInfo(option_num)
        erb_log = LogPreset(2)
        erb_log.first_log(target_name)
        for line in bulk_lines:
            line = line.strip()
            if "[SKIPEND]" in line:
                skip_start = 0
                erb_info.add_line_list(line)
                continue
            elif skip_start == 1:
                continue
            elif line.startswith(";") == True:  # 주석문
                if option_num == 1:
                    continue
                erb_info.add_line_list(line)
                continue
            elif "[SKIPSTART]" in line:
                skip_start = 1
                erb_info.add_line_list(line)
                continue
            erb_info.add_linelist_embeded(line)
        erb_log.sucessful_done()
        return erb_info

    def csv_infodict_maker(self, mod_num=0, debug_log=None):
        """infodict을 필요로하는 함수나 클래스에 사용함. debug_log은 LogPreset 타입을 요구함."""
        infodict_csv = MenuPreset().load_saved_data(
            0, "{}\n{}".format("CSV 변수 목록 추출 데이터를 불러오실 수 있습니다.", "불러오실 경우 선택하신 모드와 다르게 작동할 수 있습니다.")
        )
        if not infodict_csv:
            if mod_num in (0, 1):  # {csv파일명:{숫자:csv변수명}}
                infodict_csv = CSVFunc().import_all_CSV(0b010)
            elif mod_num == 2:  # {csv파일명:{csv변수명:숫자}}
                infodict_csv = CSVFunc().import_all_CSV(0b011)
            else:
                raise NotImplementedError(mod_num)

        if debug_log:
            if mod_num == 0:
                log_text = "작업을 위해 csv infodict 불러옴"
            elif mod_num in (1, 2):  # log_text 추가작성하는 경우
                if mod_num == 1:
                    log_text = "숫자를 index 변수로 변환"
                else:
                    log_text = "index 변수를 숫자로 변환"
                log_text = "ERB 내부 {}\n".format(log_text)
            debug_log.write_log(log_text)
        return infodict_csv

    def grammar_corrector(self, metalineinfo, mod_no=0):
        """ERBMetaInfo 기반 문법 교정기

        mod_no = bit 1: 중첩 printdata문 처리 on/off
        """
        result_lines = []
        change_dict = {}
        ch_printdata = 0
        target_metalines = metalineinfo.linelist
        for count, line in enumerate(target_metalines):
            _, _, case_count, context = line
            if context.startswith("PRINTDATA"):
                ch_printdata += 1
                if mod_no & 0b1 and ch_printdata == 1:
                    change_dict[count] = "fix_printdata/"
            elif mod_no & 0b1 and ch_printdata == 1:
                head_word = context.split()[0]
                if context.startswith("ENDDATA"):
                    ch_printdata -= 1
                    change_dict[count] = "fix_enddata/"
                elif context.startswith("DATA"):
                    if head_word == "DATALIST":
                        change_dict[count] = "fix_datalist/"
                    elif head_word in ("DATAFORM","DATA"):
                        if case_count:
                            change_dict[count] = "fix_data/fix_datalist/"
                        else:
                            change_dict[count] = "fix_data/"
                    else:
                        print("상정하지 않은 케이스 :" + context)
                elif context.startswith("ENDLIST"):
                    change_dict[count] = "delete"
            elif context.startswith("ENDDATA"):
                ch_printdata -= 1
            result_lines.append(line)

        keys = list(change_dict.keys())
        if not keys:
            print("확인된 문법 오류가 없습니다.")
            return metalineinfo
        keys.sort(reverse=True)

        case_cntdict = {}
        for key in keys:
            value = change_dict[key]
            if value == "delete":
                result_lines.pop(key)
            elif "fix" in value:
                target_line = result_lines[key]
                _, case_lv, case_count, context = target_line
                res_context = ""
                if  mod_no & 0b1 and "data" in value:
                    if "fix_data/" in value:
                        res_context += context.replace(context.split()[0], "PRINTFORMW")
                        value = value.replace("fix_data/", "")
                        if "fix_datalist/" in value:
                            context = "DATALIST"
                    if "fix_datalist/" in value:
                        no = case_count
                        if_sent = "ELSEIF A == %d" % (no - 1)
                        if no == 1:
                            if_sent = if_sent.replace("ELSEIF", "IF")
                        res_context += context.replace("DATALIST", if_sent)
                    elif value == "fix_printdata/":
                        res_context += "A = RAND:%d" % case_cntdict.pop(case_lv)
                    elif value == "fix_enddata/":
                        total_count = result_lines[key-1][2]
                        case_cntdict[case_lv] = total_count
                        res_context += context.replace("ENDDATA", "ENDIF")
                    elif value == "":
                        pass
                    else:
                        print("상정외 value :" + value)
                        res_context = context
                    
                    post_context = ""
                    if "IF" in res_context and "PRINTFORMW" in res_context:
                        res_context, post_context = res_context.split("IF")
                        if "ELSE" in res_context:
                            res_context = res_context.replace("ELSE", "")
                            post_context = "ELSEIF" + post_context
                        else:
                            post_context = "IF" + post_context
                    target_line[-1] = res_context
                    result_lines[key] = target_line
                    if post_context:
                        post_line = target_line.copy()
                        post_line[-1] = post_context
                        result_lines.insert(key, post_line)
        metalineinfo.linelist = result_lines
        return metalineinfo


class ERBVFinder:
    """문장 대응 csv 변수 필터. csvdict은 infodict형의 csv정보를 요구하며,
    log_set은 LogPreset 을 요구함
    """

    extra_dict = {
        "UP": "JUEL",
        "DOWN": "JUEL",
        "PARAM": "PALAM",
        "NOWEX": "EX",
        "UPBASE": "BASE",
        "DOWNBASE": "BASE",
    }
    context_filter = r":([^\s,\)=\+\-]+)"
    # target_list = ['TARGET','PLAYER','MASTER','ASSI'] #TODO 차원지원 필요함

    def __init__(self, csvdict :InfoDict or list, log_set=None):
        if isinstance(csvdict, InfoDict):
            self.csv_infodict = csvdict
            self.csv_fnames = dict()
            for filename in list(self.csv_infodict.dict_main.keys()):
                csvname = FileFilter().sep_filename(filename).upper()
                self.csv_fnames[csvname] = filename
            self.csv_head = list(self.csv_fnames.keys())
        elif isinstance(csvdict, list):
            self.csv_head = csvdict
        else:
            raise TypeError
        csv_all_head = self.csv_head + list(self.extra_dict.keys())
        re_varshead = "({})".format("|".join(csv_all_head))
        self.csvvar_re = re.compile(re_varshead + self.context_filter)
        self.log_set = log_set

    def find_csvfnc_line(self, line: str) -> list[tuple]:
        """해당하는 결과물이 있을 시 [(csv명,변수내용,ERB상 함수명,대명사)] 로 출력함.
        이외는 None 리턴"""
        if line.startswith(";"):
            return None
        line = line.split(";")[0]
        line_search = self.csvvar_re.findall(line)  # [(var1,arg1),(var2,arg2)...]
        find_result = []
        for var_bulk in line_search:
            var_head, var_context = var_bulk
            var_head = var_head.strip()
            var_context = var_context.strip()
            if ":" in var_context:
                var_pnoun, _, *etc = var_context.split(":")
                var_context_t = re.compile(self.context_filter).search(var_context).group(1)
                if etc:
                    print(var_bulk, "개발자에게 보고바람")
            else:
                var_pnoun = None
                var_context_t = var_context
            if self.extra_dict.get(var_head):
                var_head_t = self.extra_dict[var_head]
            else:
                var_head_t = var_head
            find_result.append((var_head_t, var_context_t, var_head, var_pnoun))
        return find_result

    def change_var_index(self, found_result: list[tuple], mod_num: int = 0):
        """find_csvfnc_line의 결과값을 받아 context을 변환한 후 다시 리스트 리턴.

        mod_num 0 : 숫자 > 단어, mod_num 1 : 단어 > 숫자
        """
        reversed_dict = self.csv_infodict.make_reverse() if self.csv_infodict.db_ver > 1.2 else None

        for res_cnt, result in enumerate(found_result):
            var_head, var_context, orig_head, p_noun = result
            int_checker = list(filter(str.isdecimal, var_context))
            if (mod_num == 0 and int_checker) or (mod_num == 1 and
                int_checker != list(var_context)
                ):
                try:
                    csv_filename = self.csv_fnames[var_head]
                    context_t = self.csv_infodict.dict_main[csv_filename].get(var_context)
                    if not context_t and reversed_dict:
                        context_t = reversed_dict[csv_filename].get(var_context)
                    found_result[res_cnt] = (var_head, (var_context, context_t),
                        orig_head, p_noun)
                except KeyError:
                    if self.log_set:
                        self.log_set.write_error_log(KeyError, orig_head)

        return found_result

    def print_csvfnc(self, comp_list: list[tuple], opt_no: int=0b0001):
        """line에서 추출된 erb내 변수 리스트를 다시 결합한 목록 리턴, 복수 가능

        opt_no bit
            1: 디폴트. erb 내 원래 형태로 출력
            2: csv에서 인식되는 형태로 출력 (대명사 포함)
            3: csv에서 인식되는 형태로 출력 (대명사 제외)
            4: (index 변환 사용시) erb 내 index 변환 행태로 출력
        """
        result_list:list[list[str]] = []
        if not comp_list:
            return result_list

        for i in range(4):
            if opt_no & (2 ** i):
                result_list.append(list())

        for fncinfo in comp_list:
            csvhead, context, orighead, pnoun = fncinfo
            if isinstance(context, tuple):
                o_context, t_context = context
                if not t_context:
                    t_context = o_context
                    if self.log_set:
                        self.log_set.write_log(
                            "{} index not found in {}".format(o_context, csvhead)
                        )
            elif isinstance(context, str):
                o_context = t_context = context
            else:
                raise NotImplementedError("잘못된 context 타입: " + str(type(context)))
            
            res_index = 0
            for i in range(4):
                temp_opt = opt_no & (2 ** i)
                if temp_opt & 0b0001:
                    head, cont = orighead, o_context
                elif temp_opt & 0b0010 or temp_opt & 0b0100:
                    head, cont = csvhead, o_context
                else: # temp_opt & 0b1000
                    head, cont = orighead, t_context
                if pnoun and temp_opt ^ 0b0100:
                    cont = pnoun + ":" + cont
                if temp_opt:
                    result_list[res_index].append("{}:{}".format(head, cont))
                    res_index += 1
    
        return result_list


class ERBBlkFinder:
    """디렉토리 대응 코드 블럭 인식 클래스"""

    def __init__(self):
        self.block_data = InfoDict(1)  # {filename:{index:(func,(code_block))}}
        self.files, self.encode_type = CustomInput("ERB").get_filelist()

    def block_maker(self):
        for filename in self.files:
            opened_erbs = ERBLoad(filename, self.encode_type)
            chk_stk = CheckStack(opened_erbs.make_erblines()).line_divider()
            self.block_data.add_dict(filename, chk_stk)
        return self.block_data

    def block_checker(self):
        # TODO 파일별/ 블럭별 분리 및 공통점(구문 위치) 확인해 변경사항 체크
        pass

    def block_showdiff(self):
        while not isinstance(self.block_data, InfoDict):
            self.block_data = MenuPreset().load_saved_data()
            if self.block_data is None:
                print("특정 디렉토리의 ERB 데이터를 불러옵니다.")
                self.block_maker()


class DataBaseERB:
    def collect_adj(self, lines:list[str], tag:str, adj_opt:bool = False, is_case:bool = False):
        result_list = []
        case_flag = False
        for line in lines:
            if is_case:
                if "ENDSELECT" in line:
                    case_flag = False
                    continue
                elif "SELECTCASE" in line:
                    case_flag = True
                    continue
                elif line.strip().startswith("CASE"):
                    for word in line.split()[1:]:
                        word = word.replace(",", "")
                        if word.isdecimal():
                            case_num = int(word)
                            continue
                    continue
            if tag in line:                
                line = line.strip()
                line = line.replace(tag, "")
                if adj_opt:
                    line = line.replace('"',"")
                    line = line.replace(r"\/", "/")
                    words = line.split("/")
                else:
                    words = [line,]
                if is_case and case_flag:
                    result_list.append((case_num, words))
                elif not is_case:
                    result_list.extend(words)
        if is_case and result_list:
            result_list = dict(result_list)
        return result_list


class ERBFunc:

    func_log = LogPreset("ERBwork")

    def __init__(self):
        self.result_infodict = InfoDict(1)

    def extract_printfunc(self, erb_files=None, encode_type=None, opt=0):
        """ERB 파일 내 출력문 데이터를 추출하는 함수
        
        opt bit 1 : 차트 내 중복 context 제거, 2: 파일당 차트 할당, 3: 공백 출력안함
        """
        print("PRINT/DATAFORM 구문의 추출을 시작합니다.")
        if not erb_files or not encode_type:
            erb_files, encode_type = CustomInput("ERB").get_filelist()
        file_count_check = StatusNum(erb_files, "파일")
        file_count_check.how_much_there()
        result_sheet = SheetInfo()
        sheet_tags = ["COM_type", "context"]
        if not opt & 0b10: # 파일당 차트 할당 아님
            sheet_tags.insert(0, "file")
            sheetname = "print_sent"
            result_sheet.add_sheet(sheetname, sheet_tags)
        if opt & 0b1: # 중복 후처리
            dup_list = list()

        for filename in erb_files:
            bulk_lines = ERBLoad(filename, encode_type)
            if opt & 0b10: # 파일당 차트 할당
                sheetname = filename
                result_sheet.add_sheet(sheetname, sheet_tags)

            if opt & 0b1000: # 주석처리 모드
                printfunc_list = [line for line in bulk_lines.make_erblines() if line.find(";")]
            else:
                printfunc_list = bulk_lines.search_line("PRINT", "DATA", except_args=["PRINTDATA","DATALIST"], opt=0b1)

            for line in printfunc_list:
                comtype = line.split()[0]
                context = " ".join(line.split()[1:])
                if opt & 0b1: # 중복 후처리
                    if dup_list.count(context):
                        continue
                    else:
                        dup_list.append(context)
                if opt & 0b100: # 공백 처리안함
                    if not context:
                        continue
    
                result_sheet.add_row(sheetname, file=filename, COM_type=comtype, context=context)
            file_count_check.how_much_done()

        CommonSent.extract_finished()
        self.func_log.sucessful_done()
        if opt & 0b1 and dup_list:
            print("중복으로 발견되어 누락 처리한 문장이 한 개 이상 존재합니다. 이후 처리에 유의해주세요.")
        return result_sheet  # SheetInfo

    def search_csv_var(self, erb_files=None, encode_type=None, opt=0):
        """ERB 파일 내 사용된 csv 변수 목록 출력
        
        opt bit 1: 참이면 CSV별 차트, 아니면 ERB별 차트
        """
        print("ERB 파일에서 사용된 CSV 변수목록을 추출합니다.")
        if not erb_files or not encode_type:
            erb_files, encode_type = CustomInput("ERB").get_filelist()
        csvvar_list = ERBUtil().csv_infodict_maker()
        if csvvar_list == None:
            try:
                csvvar_list = CSVFunc().single_csv_read("CSVfnclist.csv", opt=2)
            except:
                print("설정 정보가 없어 실행이 불가합니다.")
                return None
        vfinder = ERBVFinder(csvvar_list)
        file_count_check = StatusNum(erb_files, "파일")
        file_count_check.how_much_there()
        result_sheet = SheetInfo()
        sheet_tags = ["file", "var_name", "orig_word"]

        for filename in erb_files:
            erb_bulk = ERBLoad(filename, encode_type).make_erblines()
            self.func_log.write_loaded_log(filename)
            if not opt & 0b1: # ERB별 차트
                result_sheet.add_sheet(filename, sheet_tags)
                sheet_name = filename

            file_results = []
            for line in erb_bulk:
                vars_list = vfinder.find_csvfnc_line(line)
                if vars_list:
                    file_results.extend(vars_list)
            dup_res_list = DataFilter().dup_filter(file_results)

            for var_info in dup_res_list:
                varhead, varname, _, _ = var_info
                context = vfinder.print_csvfnc([var_info,])[0]
                if opt & 0b1:
                    sheet_name = varhead
                    if sheet_name not in result_sheet.sheetdict.keys():
                        result_sheet.add_sheet(sheet_name, sheet_tags)
                    f_name = filename
                else:
                    f_name = varhead
                result_sheet.add_row(sheet_name, file=f_name, var_name=varname, orig_word=context)
            file_count_check.how_much_done()

        CommonSent.extract_finished()
        self.func_log.sucessful_done()
        return result_sheet # SheetInfo

    def remodel_indent(self, metainfo_option_num=0, metalineinfo=None):
        if metalineinfo == None:
            print("들여쓰기를 자동 교정하는 유틸리티입니다.")
            erb_files, encode_type = CustomInput("ERB").get_filelist()
            file_count_check = StatusNum(erb_files, "파일")
            file_count_check.how_much_there()

            for filename in erb_files:
                erb_bulk = ERBLoad(filename, encode_type).make_erblines()
                lines = (
                    ERBUtil().make_metainfo_lines(erb_bulk, metainfo_option_num, filename).linelist
                )
                lines.insert(0, [0, 0, 0, ";{}에서 불러옴\n".format(filename)])
                temp_metainfo = ERBMetaInfo()
                temp_metainfo.linelist = lines
                self.result_infodict.add_dict(filename, ERBUtil().indent_maker(temp_metainfo))
                file_count_check.how_much_done()

            result_dataset = self.result_infodict  # InfoDict 클래스 {파일명:[들여쓰기 처리된 lines]}
        else:
            if isinstance(metalineinfo, list): # metaline 없는 순수 lines 일 때
                metalineinfo = ERBUtil().make_metainfo_lines(metalineinfo, metainfo_option_num)
            result_dataset = ERBUtil().indent_maker(metalineinfo)  # [들여쓰기 처리된 lines]
        CommonSent.extract_finished()
        self.func_log.sucessful_done()
        return result_dataset

    def translate_txt_to_erb(self, era_type, csvvar_dict):
        txt_files, encode_type = CustomInput("TXT").get_filelist()
        file_count_check = StatusNum(txt_files, "파일")
        file_count_check.how_much_there()
        chara_num = input("작성하실 캐릭터의 번호를 입력해주세요. : ")
        self.comp_lines = []

        for filename in txt_files:
            file_lines = ERBWrite(filename, encode_type, era_type, chara_num).txt_to_erblines(
                csvvar_dict
            )
            print("{}의 처리가 완료되었습니다.".format(filename))
            self.comp_lines.extend(file_lines)
            file_count_check.how_much_done()

        erb_metainfo = ERBUtil().make_metainfo_lines(self.comp_lines, 0, filename)
        self.func_log.sucessful_done()
        return erb_metainfo

    def replace_num_or_name(self, mod_num=0, erb_files=None, encode_type=None):
        """0:숫자 > 변수, 1: 변수 > 숫자"""
        if not erb_files or not encode_type:
            erb_files, encode_type = CustomInput("ERB").get_filelist()
        file_count_check = StatusNum(erb_files, "ERB 파일")
        file_count_check.how_much_there()
        csv_infodict = ERBUtil().csv_infodict_maker(mod_num + 1, self.func_log)
        print("ERB내 index 변환작업을 시작합니다.")

        for filename in erb_files:
            erblines = ERBLoad(filename, encode_type).make_erblines()
            replaced_lines = ERBRemodel(erblines).replace_csvvars(
                csv_infodict, mod_num
            )
            self.result_infodict.add_dict(filename, replaced_lines)
            file_count_check.how_much_done()

        CommonSent.extract_finished()
        self.func_log.sucessful_done()
        return self.result_infodict  # {파일명:[바뀐줄]}

    def remodel_equation(self, metainfo_option_num=2, metalineinfo=None):
        mod_dict = {1:"중첩 PRNTDATA 변환"}
        if metalineinfo == None:
            print("불완전한 수식을 교정해주는 유틸리티입니다.")
            erb_files, encode_type = CustomInput("ERB").get_filelist()
            file_count_check = StatusNum(erb_files, "파일")
            file_count_check.how_much_there()
            mod_no = MenuPreset().select_mod(mod_dict)

            for filename in erb_files:
                erb_bulk = ERBLoad(filename, encode_type).make_erblines()
                lines = (
                    ERBUtil().make_metainfo_lines(erb_bulk, metainfo_option_num, filename).linelist
                )
                lines.insert(0, [0, 0, 0, ";{}에서 불러옴\n".format(filename)])
                temp_metainfo = ERBMetaInfo()
                temp_metainfo.linelist = lines
                self.result_infodict.add_dict(filename, ERBUtil().grammar_corrector(temp_metainfo, mod_no))
                file_count_check.how_much_done()

            result_dataset = self.result_infodict  # InfoDict 클래스 {파일명:ERBMetaInfo 클래스 메소드}
        else:
            mod_no = MenuPreset().select_mod(mod_dict, 0b1)
            result_dataset = ERBUtil().grammar_corrector(metalineinfo, mod_no)  # ERBMetaInfo 클래스 메소드
        CommonSent.extract_finished()
        self.func_log.sucessful_done()
        return result_dataset

    def memory_optimizer(self, erb_files=None, encode_type=None):
        print("현재 기능이 완성되지 않았습니다. 되도록 백업 후 이용해주시고, 구상 파일에만 사용해주세요.")
        if not erb_files or not encode_type:
            erb_files, encode_type = CustomInput("ERB").get_filelist()
        file_count_check = StatusNum(erb_files, "파일")
        file_count_check.how_much_there()

        for filename in erb_files:
            erblines = ERBLoad(filename, encode_type).make_erblines()
            optmized_lines = ERBRemodel(erblines).memory_optimize()
            self.result_infodict.add_dict(filename, optmized_lines)
            file_count_check.how_much_done()

        CommonSent.extract_finished()
        self.func_log.sucessful_done()
        return self.result_infodict  # {파일명:lines} 형태가 포함된 infodict

    def erb_trans_helper(self):  # TODO 공사중
        """번역본의 원본 이식에 도움을 주는 함수"""
        print("원본 erb의 디렉토리를 지정해주세요.")
        o_blkdata = ERBBlkFinder()
        print("번역본 erb의 디렉토리를 지정해주세요.")
        t_blkdata = ERBBlkFinder()
        # TODO 이름만 다른 파일 비교 가능하게 - CompareErb.csv 활용

    def db_erb_finder(self, erb_files=None, encode_type=None, tag=None):
        """데이터베이스형 ERB 자료 추출 함수"""
        print("되도록 필요한 파일만 있는 폴더를 만든 후 그곳에서 진행해주세요.",
        "추후 복수의 파일을 비교하고자 하는 경우, 각 파일의 파일명은 같아야 합니다.",
        sep="\n"
        )
        if not erb_files or not encode_type:
            erb_files, encode_type = CustomInput("ERB").get_filelist()
        while True:
            if not tag:
                tag = input("필요한 데이터 형식의 앞말을 붙여넣어주세요.: ")
            adj_yn = MenuPreset().yesno(
                "AAA/BBB/CCC 꼴의 데이터인 경우, 각 요소별 분할이 가능합니다.",
                "분할을 시도하시겠습니까?")
            case_yn = MenuPreset().yesno(
                "CASE XXX ~ tag AAA 꼴의 데이터인 경우 CASE를 활용한 좀 더 정확한 계산이 가능합니다.",
                "해당 작업을 시도하시겠습니까?")
            adj_res = "Yes" if adj_yn else "No"
            case_res = "Yes" if case_yn else "No"
            if not MenuPreset().yesno("tag: %s, 분할 시도: %s, CASE 사용: %s가 맞습니까?" % (tag, adj_res, case_res)):
                if MenuPreset().yesno("작업을 취소할까요?"):
                    return None
                continue
            break

        for erbname in erb_files:
            erb_load = ERBLoad(erbname, encode_type)
            erblines = erb_load.make_erblines()
            self.result_infodict.add_dict(erbname, DataBaseERB().collect_adj(erblines, tag, adj_yn, case_yn))

        return self.result_infodict
