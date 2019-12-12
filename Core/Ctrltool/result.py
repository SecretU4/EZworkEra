"""EZworkEra에서 생성된 데이터를 출력하는데 사용되는 모듈.

Classes:
    ExportData
    ResultFunc
"""
import os
from customdb import ERBMetaInfo, InfoDict
from usefile import DirFilter, FileFilter, LoadFile, MakeLog, MenuPreset
from util import DataFilter
from System.interface import Menu


class ExportData:
    """입력받은 데이터를 특정 파일 양식에 맞게 출력하는 클래스.

    Functions:
        to_TXT([filetype,option_num,encode_type])
        to_SRS([srsname])
    """
    def __init__(self,dest_dir,target_name,target_data):
        self.dest_dir = dest_dir # 결과물 저장 폴더
        self.target_name = target_name
        self.target_data = target_data
        self.lazy_switch = 0 # 데이터 미선택한 경우 1
        self.log_file = MakeLog('export_debug.log')

    single_namedict = {'ONLYONE':None,'ONLYDICT':dict,
                        'ONLYLIST':list,'ONLYMETALINES':ERBMetaInfo}

    def __multi_data_input(self):
        """입력받는 데이터가 2개인 경우 사용. sav 디랙토리의 저장 파일을 불러옴."""
        if bool(self.target_data) == True:
            print("현 구동 중 실행된 데이터의 종류를 입력해주세요.")
            origin_switch = MenuPreset(
            ).yesno("실행된 데이터는 번역문인가요? 아니라면 원문으로 간주합니다.")
            if origin_switch == 0:
                trans_data = self.target_data
                print("원본 데이터를 불러와주세요.")
                orig_data = MenuPreset().load_saved_data(1)
            elif origin_switch == 1:
                orig_data = self.target_data
                print("번역본 데이터를 불러와주세요.")
                trans_data = MenuPreset().load_saved_data(1)
        else:
            print("원본 데이터를 불러와주세요.")
            orig_data = MenuPreset().load_saved_data(1)
            print("번역본 데이터를 불러와주세요.")
            trans_data = MenuPreset().load_saved_data(1)
        return orig_data,trans_data

    def __data_type_check(self,*data_names):
        """입력받은 데이터 체크 후 InfoDict.dict_main 형으로 출력"""
        checked_datalist = []
        for data in data_names:
            if isinstance(data,InfoDict) == True: # InfoDict 자료형인 경우
                dict_data_vals = list(data.dict_main.values()) # InfoDict 결과물이라면 각 사전 데이터임.
                if os.path.isfile(list(data.dict_main.keys())[0]) == True: # InfoDict 결과물인지 체크
                    # {파일명, csv딕셔너리 구조}
                    if isinstance(dict_data_vals[0],dict) == True:
                        checked_datalist.append(data.dict_main)
                    # {파일명, 리스트 구조}
                    elif isinstance(dict_data_vals[0],list) == True:
                        checked_datalist.append(data.dict_main)
                    # {파일명, ERB메타라인 구조}
                    elif isinstance(dict_data_vals[0],ERBMetaInfo) == True:
                        checked_datalist.append(data.dict_main)
                    else:
                        print("InfoDict 내부에 정의되지 않은 자료형이 있습니다.")
                        self.log_file.write_log(
                            "올바르지 않은 자료형({})이 InfoDict에 포함되어 있습니다.".format(type(data)))
                        checked_datalist.append(None)
            elif isinstance(data,ERBMetaInfo) == True:
                checked_datalist.append({'ONLYMETALINES':data.linelist})
            elif isinstance(data,dict) == True: # InfoDict 결과물이 아닌 순수 dict
                    checked_datalist.append({'ONLYDICT':data})
            elif isinstance(data,list) == True: # list 자료형
                checked_datalist.append({'ONLYLIST':data})
            else: # 자료형이 InfoDict, ERBMetaInfo, dict, list 아님
                print("입력된 데이터가 유효한 데이터가 아닙니다.")
                print("{} 타입 자료형입니다.".format(type(data)))
                checked_datalist.append(None)
        return checked_datalist # [{InfoDict.dict_main},{InfoDict.dict_main}...]

    def __SRS_multi_write(self,orig_dict,trans_dict,keyname):
        """SRS용 교차출력 함수. 유효하지 않은 내용 판단이 동시에 이루어짐."""
        if orig_dict == None or trans_dict == None:
            print("SRS를 작성할 수 없습니다.")
            return None
        with LoadFile(self.srs_filename).addwrite() as srs_file:
            srs_file.write(';이하 {0}\n\n'.format(keyname))
            orig_keys = list(orig_dict.keys())
            trans_keys = list(trans_dict.keys())
            total_keys = DataFilter().dup_filter(orig_keys+trans_keys)
            for total_key in total_keys:
                if total_key in orig_keys and total_key in trans_keys:
                    srs_file.write("{}\n{}\n\n".format(orig_dict[total_key],trans_dict[total_key]))
                else:
                    if total_key not in orig_keys:
                        error_dictname = self.orig_dictname
                    elif total_key not in trans_keys:
                        error_dictname = self.trans_dictname
                    self.srslog_file.write("{}번 숫자가 {}에 존재하지 않습니다.\n".format(total_key,error_dictname))
                    srs_file.write(";{}번확인필요\n\n".format(total_key))
                    self.cantwrite_srs_count += 1

    def to_TXT(self,filetype='txt',option_num=0,encode_type='UTF-8'):
        """입력받은 데이터를 텍스트 파일 형태로 출력하는 함수.
        """
        # txt, erb 공용
        # erb metaline은 ERBFilter.indent_maker에서 텍스트.readlines형으로 양식화됨
        if self.target_data == None:
            print("미리 실행된 자료가 없습니다.")
            print_data = MenuPreset()
            self.target_data = print_data.load_saved_data()
            if self.target_data == None: self.lazy_switch = 1
            else:
                result_filename = FileFilter(2).sep_filename(
                                        print_data.selected_name)+'.'+filetype
                self.target_name = print_data.selected_name
        else:
            print("이번 구동 중 실행된 {} 자료를 {}화 합니다.".format(self.target_name,filetype))
            result_filename = self.target_name+'.'+filetype
        if self.lazy_switch == 1:
            print("데이터가 선택되지 않았습니다.")
            return 0
        else:
            checked_data = self.__data_type_check(self.target_data) # [{infodict},{infodict}]
            checked_data.append({"돌아가기":"돌아가기"})
            chk_data_listdict = {}
            for data in checked_data:
                chk_data_listdict[checked_data.index(data)]=list(data.keys())[0]
            menu_chk_datalist = Menu(chk_data_listdict)
            chkdata_no = menu_chk_datalist.run_menu()
            selected_infodict = chk_data_listdict[chkdata_no]
            if list(selected_infodict)[0] == "돌아가기": return 0
            #TODO 복수의 InfoDict 데이터를 불러온 경우의 지원
            unpacked_data = list(checked_data[0].values())
            with LoadFile(self.dest_dir+result_filename,encode_type).readwrite() as txt_file:
                txt_file.write("{}에서 불러옴\n".format(self.target_name))
                for context in unpacked_data:
                    if option_num == 0:
                        print("{}\n".format(context),file=txt_file)
                    elif option_num == 1:
                        if type(context) == list: txt_file.writelines(context)
                        else: print("텍스트화 할 수 없는 데이터입니다. 옵션을 바꿔 다시 시도해주세요.")

    def to_SRS(self,srsname='autobuild'):
        self.cantwrite_srs_count = 0
        while True:
            dataset = self.__multi_data_input()
            orig_dictinfo, trans_dictinfo, *_ = self.__data_type_check(*dataset)
            if orig_dictinfo and trans_dictinfo: break
            print("공란인 데이터가 있습니다. 다시 시도해주세요.")
        self.srs_filename = '{}.simplesrs'.format(self.dest_dir+srsname)
        if bool(orig_dictinfo) == False or bool(trans_dictinfo) == False: self.lazy_switch = 1
        else:
            with LoadFile('srs_debug.log').readwrite() as self.srslog_file:
                orig_dictnames = list(orig_dictinfo.keys())
                trans_dictnames = list(trans_dictinfo.keys())
                if os.path.isfile(self.srs_filename) == False: # SRS 유무 검사
                    print("SRS 파일을 새로 작성합니다.")
                    with LoadFile(self.srs_filename,'UTF-8-sig').readwrite() as srs_file:
                        wordwrap_yn = 1
                        for dictname in orig_dictnames:
                            if 'chara' in dictname or 'name' in dictname:
                                print("이름 관련 파일명이 감지되었습니다.")
                                wordwrap_yn = MenuPreset().yesno(
                                    "입력받은 데이터 전체를 정확한 단어 단위로만 변환하도록 조정할까요?")
                                break
                        if wordwrap_yn != 0: srs_file.write("[-TRIM-][-SORT-]\n\n")
                        else: srs_file.write("[-TRIM-][-SORT-][-WORDWRAP-]\n\n")
                        # TRIM:앞뒤공백 제거, SORT:긴 순서/알파벳 정렬, WORDWRAP:정확히 단어 단위일때만 치환
                for num in range(len(orig_dictinfo)):
                    try:
                        self.orig_dictname = orig_dictnames[num]
                        self.trans_dictname = trans_dictnames[num]
                    except IndexError as error:
                        self.srslog_file.write("{}에서 {} 발생.".format(orig_dictnames[num],error))
                        self.cantwrite_srs_count += 1
                        continue
                    if self.orig_dictname in list(ExportData.single_namedict) : keyname = "단독파일"
                    else: keyname = FileFilter().sep_filename(self.orig_dictname)
                    if keyname.lower() != FileFilter().sep_filename(self.trans_dictname).lower():
                        self.trans_dictname = FileFilter(
                            ).search_filename_wordwrap(trans_dictnames,keyname.split())
                        if self.trans_dictname == None:
                            self.cantwrite_srs_count += 1
                            self.srslog_file.write("키워드: {} 불일치 존재.\n\n".format(keyname))
                            continue
                        self.srslog_file.write("{}번째부터 순서 불일치로 추가탐색 진행함.\n".format(num))
                    orig_valdict = orig_dictinfo.get(self.orig_dictname)
                    trans_valdict = trans_dictinfo.get(self.trans_dictname)
                    self.__SRS_multi_write(orig_valdict,trans_valdict,keyname)
                    # 이 단계에서 들어오는 valdict = {숫자, 데이터} 형식
            if self.cantwrite_srs_count != 0:
                print("{}쌍의 데이터가 정확히 작성되지 못했습니다. srsdebug.log를 확인해주세요.".format(
                                                                    self.cantwrite_srs_count))


class ResultFunc:
    """입력받은 정보를 바탕으로 ExportData를 활용하는 취합용 클래스.

    Functions:
        make_result(target_name,target_data,[result_type])
    """
    def make_result(self,target_name,target_data,result_type=0):
        """입력받은 정보를 ExportData에 전달하는 함수.

        Factors:
            target_name
                출력될 파일의 이름
            target_data
                출력될 데이터
            result_type
                출력될 파일의 확장자 타입. 0:txt, 1:erb, 2:srs 이고 미입력시 txt가 출력됨.
        """
        dirname = DirFilter('ResultFiles').dir_exist()
        result_file = ExportData(dirname,target_name,target_data)
        if result_type == 0:
            print("지정된 데이터의 TXT 파일화를 진행합니다.")
            press_enter_yn = MenuPreset(
                ).yesno("데이터에 줄바꿈이 되어있던 경우, 줄바꿈 출력이 가능합니다. 시도하시겠습니까?")
            if press_enter_yn == 0: result_file.to_TXT(option_num=1)
            else: result_file.to_TXT()
        elif result_type == 1:
            print("지정된 데이터의 ERB 파일화를 진행합니다.")
            result_file.to_TXT('erb',1,'UTF-8-sig')
        elif result_type == 2:
            print("csv 변수로 작성시 chara 폴더가 제외되어있어야 합니다.")
            print("작성 또는 수정할 srs 파일명을 입력해주세요.")
            srs_name = input("공란일 시 autobuild.simplesrs로 진행합니다. :")
            if bool(srs_name) == False: result_file.to_SRS()
            else: result_file.to_SRS(srs_name)
        if result_file.lazy_switch == 1:
            print("파일 처리를 진행하지 못했습니다.")
        else:
            print("처리가 완료되었습니다.")
        input("엔터를 눌러 계속...")

#TODO MakeLog 클래스 이식
