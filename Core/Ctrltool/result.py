"""EZworkEra에서 생성된 데이터를 출력하는데 사용되는 모듈.

Classes:
    ExportData
    SubFilter
    ResultFunc
"""
import re
import os
from customdb import ERBMetaInfo, InfoDict
from usefile import DirFilter, FileFilter, LoadFile, LogPreset, MenuPreset
from util import CommonSent, DataFilter
from System.interface import Menu, StatusNum
from . import CSVFunc, ERBFunc


class ExportData:
    """입력받은 데이터를 특정 파일 양식에 맞게 출력하는 클래스.

    Functions:
        to_TXT([filetype,option_num,encode_type])
        to_SRS([srs_opt, srsname])
    Vairables:
        dest_dir: 결과물 저장 폴더
        target_name: 입력받은 데이터 이름
        target_data: 입력받은 데이터
        lazy_switch: 데이터 미선택시 켜짐. 작업 진행 확인용
        log_file: 로그파일 생성용 LogPreset
    Misc:
        single_namedict
            파일 확인 절차에서 infodict형을 받지 않았을 시 출력되는 데이터 이름사전
    """

    single_namedict = {
        None: "None",
        dict: "ONLYDICT",
        str: "ONLYSTRING",
        list: "ONLYLIST",
        ERBMetaInfo: "ONLYMETALINES",
    }

    def __init__(self, dest_dir, target_name, target_data):
        self.dest_dir = dest_dir  # 결과물 저장 폴더
        self.target_name = target_name
        self.target_data = target_data
        self.lazy_switch = 0  # 데이터 미선택한 경우 1
        self.log_file = LogPreset(4)  # 중간에 workclass 바꾸는 경우 있어 초기화 필요

    def __multi_data_input(self, data_count=2):
        """입력받는 데이터가 2개인 경우 사용. sav 디랙토리의 저장 파일을 불러옴."""
        result_input = []
        if self.target_data:
            result_input.append(self.target_data)
            print("직전에 실행한 데이터를 목록에 추가합니다.")
            data_count -= 1
        inputed_count = 1
        for _ in range(data_count):
            result_input.append(
                MenuPreset().load_saved_data(
                    1, "{}개 중 {}번째 파일을 불러옵니다.".format(data_count, inputed_count)
                )
            )
            inputed_count += 1
        return tuple(result_input)

    def __data_type_check(self, mod_no, *data_names):
        """입력받은 데이터 체크 후 인터페이스 선택 후 tuple 요소로 된 list 출력"""
        checked_datadict = dict()
        for data in data_names:
            if isinstance(data, InfoDict):  # InfoDict 자료형인 경우
                try:
                    if data.db_ver > 1.1:
                        data_tag = data.db_name
                    else:
                        data_tag = "OldVersion"
                except AttributeError as aterror:
                    data_tag = "N/A"
                    self.log_file.write_error_log(aterror)
                dict_data_vals = list(data.dict_main.values())  # InfoDict 결과물이라면 dict 데이터 list임.
                if isinstance(dict_data_vals[0], (dict, list, ERBMetaInfo)) == True:
                    tagging_data = {
                        "All {} - {} etc.".format(data_tag, list(data.dict_main.keys())[0]): data
                    }
                else:
                    print("InfoDict 내부에 정의되지 않은 자료형이 있습니다.")
                    self.log_file.write_log(
                        "올바르지 않은 자료형({})이 InfoDict에 포함되어 있습니다.\n".format(type(data))
                    )
                    tagging_data = {"None": None}
            elif isinstance(data, (dict, list, str, ERBMetaInfo)):
                tagging_data = {self.single_namedict[type(data)]: data}
            else:  # 자료형이 InfoDict, ERBMetaInfo, dict, list 아님
                print("입력된 데이터가 유효한 데이터가 아닙니다.")
                print("{} 타입 자료형입니다.".format(type(data)))
                self.log_file.write_log("유효한 데이터 아님 - {} 타입 자료형\n".format(type(data)))
                tagging_data = {"None": None}
            checked_datadict.update(tagging_data)

        # 이하 분리 가능(자료 목록화 기능 담당)
        datasearch_dicts = checked_datadict.copy()  # {자료tag:data, 자료tag:data}
        for tag_key in list(checked_datadict.keys()):
            val_data = checked_datadict[tag_key]
            if tag_key in list(self.single_namedict.values()):
                continue
            elif isinstance(val_data, InfoDict):
                datasearch_dicts.update(val_data.dict_main)

        chklist_for_menu = list(datasearch_dicts.keys())
        menu_chk_datalist = Menu(chklist_for_menu)
        final_list = []
        selected_name_list = []
        while True:
            menu_chk_datalist.title(
                "출력할 데이터를 원하시는 만큼 선택해주세요.",
                "ALL ~ etc 라 표기된 항목은 표기된 자료가 포함된 전체를 뜻합니다.",
                "모두 고르셨다면 돌아가기를 눌러주세요.",
            )
            selected_num = menu_chk_datalist.run_menu()
            selected_menu = menu_chk_datalist.selected_menu
            if selected_menu == "돌아가기":
                break
            final_list.append((selected_menu, datasearch_dicts[chklist_for_menu[selected_num]]))
            if len(final_list) >= 2 and mod_no == 1:
                break
            selected_name_list.append(selected_menu)
            menu_chk_datalist.title(
                "선택된 데이터 수 : {} 개".format(len(final_list)), "선택된 데이터 : ", *selected_name_list
            )
        return tuple(final_list)  # ((tag,data),(tag,data))

    def __SRS_multi_write(self, data_orig, data_trans, keyname, opt_no=0):
        """SRS용 교차출력 함수. 유효하지 않은 내용 판단이 동시에 이루어짐."""
        self.worked_switch = 0
        error_target = []
        if data_orig == None or data_trans == None:
            if data_trans == None:
                error_target.append(self.trans_key)
            if data_orig == None:
                error_target.append(self.orig_key)
            self.log_file.write_log("{} 자료를 이용한 SRS를 작성할 수 없습니다.".format("자료와 ".join(error_target)))
            return 0

        with LoadFile(self.srs_filename).addwrite() as srs_file:
            srs_file.write(";이하 {0}\n\n".format(keyname))
            self.log_file.write_log(keyname + " 정보를 불러옴\n")
            if self.infodict_switch:
                if isinstance(data_orig, dict) and isinstance(data_trans, dict):
                    # CSV 변수목록
                    orig_keys = list(data_orig.keys())
                    trans_keys = list(data_trans.keys())
                    total_keys = DataFilter().dup_filter(orig_keys + trans_keys)
                    dict_switch = 1
                elif isinstance(data_orig, list) and isinstance(data_trans, list):
                    # ERB lines
                    orig_keys = data_orig
                    trans_keys = data_trans
                    total_keys = range((len(data_orig) + len(data_trans) / 2))
                    dict_switch = 0
            else:
                orig_keys = data_orig
                trans_keys = data_trans
                total_keys = range((len(data_orig) + len(data_trans) / 2))
                dict_switch = 0

            if not dict_switch and len(total_keys) != (len(data_orig) + len(data_trans)):
                print("줄의 개수가 맞지 않아 오류가 발생할 수 있습니다.")
                self.log_file.write_log("두 자료의 행 개수 맞지 않음\n")

            for total_key in total_keys:
                if total_key in orig_keys and total_key in trans_keys:
                    if data_orig[total_key].strip() == "" and data_trans[total_key].strip() == "":
                        self.log_file.write_log("{}번 숫자의 내용이 빈칸입니다.\n".format(total_key))
                        self.cantwrite_srs_count += 1
                        continue
                    orig_text = data_orig[total_key]
                    trans_text = data_trans[total_key]
                elif dict_switch:
                    if total_key not in orig_keys:
                        error_dictname = self.orig_key
                    elif total_key not in trans_keys:
                        error_dictname = self.trans_key
                    self.log_file.write_log(
                        "{}번 숫자가 {}에 존재하지 않습니다.\n".format(total_key, error_dictname)
                    )
                    srs_file.write(";숫자 {} 확인필요\n\n".format(total_key))
                    self.cantwrite_srs_count += 1
                    continue
                else:
                    orig_text = orig_keys[total_key].strip()
                    trans_text = trans_keys[total_key].strip()

                try:  # 중복변수 존재 유무 검사
                    self.for_dup_content.index(orig_text)
                except ValueError:
                    self.for_dup_content.append(orig_text)
                    if opt_no == 1:
                        if orig_text == trans_text:
                            continue
                        elif len(orig_text) < 2:
                            self.log_file.write_log(
                                "단어가 너무 짧습니다 : {}번째 항목의 {}\n".format(total_key, orig_text)
                            )
                            self.cantwrite_srs_count += 1
                            continue
                    srs_file.write("{}\n{}\n\n".format(orig_text, trans_text))
                    self.worked_switch = 1

        if not self.worked_switch:
            self.log_file.write_log("전체 중복 또는 오류로 인해 자료 전체 통과됨\n")

    def to_TXT(self, filetype="TXT", option_num=0, encode_type="UTF-8"):
        """입력받은 데이터를 텍스트 파일 형태로 출력하는 함수.

        Vairables:
            filetype: 확장자 구분
            option_num: 1이면 출력시 줄바꿈 관련 절차 진행
            encode_type: 저장되는 파일의 인코딩
        """
        # txt, erb 공용
        # erb metaline은 ERBUtil.indent_maker에서 텍스트.readlines형으로 양식화됨
        self.log_file.workclass = "TXTwrite"
        if self.target_data == None:
            print_data = MenuPreset()
            self.target_data = print_data.load_saved_data(0, "미리 실행된 자료가 없습니다.")
            if self.target_data == None:
                print("데이터가 선택되지 않았습니다.")
                self.lazy_switch = 1
                return 0
            else:
                self.target_name = print_data.selected_name
        else:
            print("이번 구동 중 실행된 {} 자료를 {}화 합니다.".format(self.target_name, filetype))
        target_data = self.__data_type_check(0, self.target_data)  # ((자료명,알수 없는 자료형),...)
        menu_dict_sel_dest = {0: "원본 위치에 저장", 1: "결과물 폴더에 저장"}
        menu_sel_dest = Menu(menu_dict_sel_dest)
        menu_sel_dest.title(
            "변환된 파일을 어떤 위치에 저장할까요?",
            "원본 폴더에 저장시 원본 데이터가 손상될 수 있습니다.",
            "결과물 데이터에 원본 위치 정보가 없다면 오류가 발생합니다.",
        )
        dest_mod = menu_sel_dest.run_menu()

        que_list = []
        for data in target_data:
            tag, content = data
            if isinstance(content, InfoDict):
                infodict = content.dict_main
                sel_data = list(map(lambda x: {x: infodict[x]}, infodict.keys()))
            elif isinstance(content, ERBMetaInfo):
                sel_data = [{tag: content.linelist}]
            elif isinstance(content, (list, dict)):
                sel_data = [{tag: content}]
            else:
                print("상정되지 않은 자료형이나 일단 진행합니다.")
                sel_data = [data]
            que_list.extend(sel_data)  # [{tag:content}]
        numstat = StatusNum(que_list, filetype + " 파일자료")
        numstat.how_much_there()

        for que in que_list:
            data_filename = list(que.keys())[0]
            if dest_mod == 1:  # 결과물 디렉토리에 저장
                if len(que_list) == 1 and data_filename in list(self.single_namedict.values()):
                    data_filename = "({}){}".format(CommonSent.put_time(1), self.target_name)
                result_filename = "{}.{}".format(FileFilter().sep_filename(data_filename), filetype)
                the_filename = self.dest_dir + result_filename
            elif dest_mod == 0:  # 원본 디렉토리에 저장
                the_filename = data_filename
            self.log_file.which_type_loaded(filetype)

            with LoadFile(the_filename, encode_type).readwrite() as txt_file:
                if filetype == "TXT":
                    txt_file.write("{}에서 불러옴\n".format(self.target_name))
                context = que[data_filename]
                if type(context) == dict:
                    for key in list(context.keys()):
                        print("{}:{}".format(key, context[key]), file=txt_file)
                elif option_num == 0:
                    print("{}\n".format(context), file=txt_file)
                elif option_num == 1:
                    if type(context) == list:
                        txt_file.writelines(context)
                    elif isinstance(context, ERBMetaInfo):
                        the_lines = ERBFunc().remodel_indent(target_metalines=context.linelist)
                        txt_file.writelines(the_lines)
                    else:
                        print("텍스트화 할 수 없는 데이터입니다. 옵션을 바꿔 다시 시도해주세요.")
                        self.log_file.write_log("Can not write text by {}".format(type(context)))
            numstat.how_much_done()
        self.log_file.sucessful_done()

    def to_SRS(self, srs_opt=0, srsname="autobuild"):
        """입력받은 데이터를 updateera의 simplesrs 양식으로 출력

        Variables:
            srs_opt: 1이면 짧은 단어, srs 내부 중복 문자열 필터링
            srsname: 저장될 simplesrs 파일명
        """
        total_worked_switch = 0
        self.log_file.workclass = "SRSWrite"
        self.cantwrite_srs_count = 0
        while True:
            dataset = self.__multi_data_input()
            print("처음 선택한 두 데이터만으로 진행합니다.\n")
            print("SRS 자료 입력시 첫번째를 원문, 두번째를 번역문으로 인식합니다.\n")
            orig_dataset, trans_dataset, *_ = self.__data_type_check(
                1, *dataset
            )  # ((tag,data),(tag,data))
            orig_data, trans_data = orig_dataset[1], trans_dataset[1]
            if orig_data and trans_data:
                choose_yn = MenuPreset().yesno(
                    0,
                    "선택하신 두 자료가",
                    "원본:  " + str(orig_dataset[0]),
                    "번역본: " + str(trans_dataset[0]),
                    "입니까?",
                )
                if choose_yn == 0:
                    break
            else:
                print("공란인 데이터가 있습니다. 다시 시도해주세요.")
        self.srs_filename = "{}.simplesrs".format(self.dest_dir + srsname)
        if bool(orig_data) == False or bool(trans_data) == False:
            self.lazy_switch = 1
            return 0
        elif isinstance(orig_data, InfoDict) and isinstance(trans_data, InfoDict):
            orig_infokeys = list(orig_data.dict_main.keys())
            trans_infokeys = list(trans_data.dict_main.keys())
            self.infodict_switch = 1
        else:
            orig_infokeys = [orig_dataset[0]]
            trans_infokeys = [trans_dataset[0]]
            self.infodict_switch = 0
        if os.path.isfile(self.srs_filename) == False:  # SRS 유무 검사
            print("SRS 파일을 새로 작성합니다.")
            with LoadFile(self.srs_filename, "UTF-8-sig").readwrite() as srs_file:
                wordwrap_yn = None
                if isinstance(orig_data, InfoDict) and isinstance(trans_data, InfoDict):
                    for dictname in orig_infokeys:
                        if "chara" in dictname or "name" in dictname:
                            print("이름 관련 파일명이 감지되었습니다.")
                            wordwrap_yn = MenuPreset().yesno(
                                0, "입력받은 데이터 전체를 정확한 단어 단위로만 변환하도록 조정할까요?"
                            )
                            break
                # TRIM:앞뒤공백 제거, SORT:긴 순서/알파벳 정렬, WORDWRAP:정확히 단어 단위일때만 치환
                if wordwrap_yn:
                    srs_file.write("[-TRIM-][-SORT-][-WORDWRAP-]\n\n")
                else:
                    srs_file.write("[-TRIM-][-SORT-]\n\n")
                self.for_dup_content = []
        else:
            with LoadFile(self.srs_filename, "UTF-8-sig").readonly() as srs_preread:
                bulk_srs = srs_preread.read()
                self.for_dup_content = SubFilter().srs_check_dup(bulk_srs)
        print("SRS 입력을 시작합니다...")
        for num in range(len(orig_infokeys)):
            try:
                self.orig_key = orig_infokeys[num]
                self.trans_key = trans_infokeys[num]
            except IndexError as error:
                comment = "두 자료의 항목 수 또는 행이 같지 않습니다."
                self.log_file.write_error_log(error, self.orig_key, comment)
                self.cantwrite_srs_count += 1
                continue
            if self.orig_key in list(ExportData.single_namedict.values()):
                keyname = "단독파일"
            else:
                keyname = FileFilter().sep_filename(self.orig_key)

            if keyname.lower() != FileFilter().sep_filename(self.trans_key).lower():
                # orig_key와 trans_key가 일치하지 않을때
                self.trans_key = FileFilter().search_filename_wordwrap(
                    trans_infokeys, keyname.split()
                )
                if self.trans_key == None:
                    self.cantwrite_srs_count += 1
                    self.log_file.write_log("키워드: {} 불일치 존재.\n\n".format(keyname))
                    continue
                self.log_file.write_log("{}번째부터 순서 불일치로 추가탐색 진행함.\n".format(num))
            if self.infodict_switch:
                target_orig = orig_data.dict_main.get(self.orig_key)
                target_trans = trans_data.dict_main.get(self.trans_key)
            else:
                target_orig = orig_data
                target_trans = trans_data
            self.__SRS_multi_write(target_orig, target_trans, keyname, srs_opt)
            total_worked_switch += self.worked_switch
        if total_worked_switch and self.cantwrite_srs_count == 0:
            pass
        else:
            if not total_worked_switch:
                print("입력된 정보로 이전에 만들어진 SRS 파일이거나 오류로 인해 SRS의 가필이 이루어지지 않았습니다.")
            elif self.cantwrite_srs_count != 0:
                print("{}쌍의 데이터가 정확히 작성되지 못했습니다.".format(self.cantwrite_srs_count))
            print("{}를 확인해주세요.".format(self.log_file.NameDir))
        self.log_file.sucessful_done()


class SubFilter:
    """필요시 타 모듈에서 사용 가능한 필터를 제공하는 모듈

    Functions:
        srs_check_dup(textbulk)
    Misc:
        wholeword: re 모듈용 필터. r'[^,;\\r\\n]+'
    """

    wholeword = r"[^,;\r\n]+"

    def srs_check_dup(self, textbulk):
        """이미 존재하는 srs 내의 original 문자열 데이터 list화"""
        srs_textfilter = re.compile("{1}({0}){1}({0}){1}".format(self.wholeword, os.linesep))
        found_list = list(map(lambda x: x[0], srs_textfilter.findall(textbulk)))
        return DataFilter().dup_filter(found_list)


class ResultFunc:
    """입력받은 정보를 바탕으로 ExportData를 활용하는 취합용 클래스.

    Functions:
        make_result(target_name,target_data,[result_type])
    """

    def make_result(self, target_name, target_data, result_type=0):
        """입력받은 정보를 ExportData에 전달하는 함수.

        Factors:
            target_name
                출력될 파일의 이름
            target_data
                출력될 데이터
            result_type
                출력될 파일의 확장자 타입. 0:txt, 1:erb, 2:srs 이고 미입력시 txt가 출력됨.
        """
        dirname = DirFilter("ResultFiles").dir_exist()
        result_file = ExportData(dirname, target_name, target_data)
        if result_type == 0:
            print("지정된 데이터의 TXT 파일화를 진행합니다.")
            press_enter_yn = MenuPreset().yesno(1, "데이터에 줄바꿈이 되어있던 경우, 줄바꿈 출력이 가능합니다. 시도하시겠습니까?")
            result_file.to_TXT(option_num=press_enter_yn)
        elif result_type == 1:
            print("지정된 데이터의 ERB 파일화를 진행합니다.")
            result_file.to_TXT("ERB", 1, "UTF-8-sig")
        elif result_type == 2:
            print("지정된 데이터의 SRS 파일화를 진행합니다.")
            print("csv 변수로 작성시 chara 폴더가 제외되어있어야 합니다.")
            print("ERB 데이터로 시도시 두 자료의 행 위치가 일치해야 합니다.")
            print("작성 또는 수정할 srs 파일명을 입력해주세요.")
            srs_name = input("공란일 시 autobuild.simplesrs로 진행합니다. :")
            optimize_srs_yn = MenuPreset().yesno(1, "미번역 단어 제외, 짧은 단어 제외 등의 기능을 사용하시겠습니까?")
            if srs_name:
                result_file.to_SRS(optimize_srs_yn, srs_name)
            else:
                result_file.to_SRS(optimize_srs_yn)
        if result_file.lazy_switch == 1:
            print("파일 처리를 진행하지 못했습니다.")
        else:
            print("처리가 완료되었습니다.")
        input("엔터를 눌러 계속...")
