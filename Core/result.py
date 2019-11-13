# 생성된 결과물 처리 모듈
import os
from util import DataFilter, DirCheck, LoadFile, MenuPreset


class ExportData:
    def __init__(self,dest_dir,target_name,target_data):
        self.dest_dir = dest_dir # 결과물 저장 폴더
        self.target_name = target_name
        self.target_data = target_data
        self.lazy_switch = 0 # 데이터 미선택한 경우 1

    def __multi_data_input(self): # 작성시 필요 데이터 2개일때
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

    def to_TXT(self,filetype='txt'): # txt, erb 공용
        if self.target_data == None:
            print("미리 실행된 자료가 없습니다.")
            print_data = MenuPreset()
            target_data = print_data.load_saved_data()
            if target_data == None:
                self.lazy_switch = 1
            else:
                result_filename = DataFilter().sep_filename(
                                        print_data.savfile_name,2)+'.'+filetype
                target_name = print_data.savfile_name
        else:
            print("이번 구동 중 실행된 {} 자료를 {}화 합니다.".format(self.target_name,filetype))
            result_filename = self.target_name+'.'+filetype
            target_name = self.target_name
            target_data = self.target_data
        if self.lazy_switch == 1: pass
        else:
            with LoadFile(self.dest_dir+result_filename).readwrite() as txt_file:
                txt_file.write("{}에서 불러옴\n".format(target_name))
                print(target_data,file=txt_file)

    def to_SRS(self,srsname='autobuild'):
        self.cantwrite_srs_count = 0
        orig_dictinfo ,trans_dictinfo =self.__SRS_dict_type_check() # {분류명 : 딕셔너리} 구조화
        self.srs_filename = '{}.simplesrs'.format(self.dest_dir+srsname)
        if bool(orig_dictinfo) == False or bool(trans_dictinfo) == False: self.lazy_switch = 1
        else:
            with LoadFile('srsdebug.log').readwrite() as self.srslog_file:
                if os.path.isfile(self.srs_filename) == False:
                    print("SRS 파일을 새로 작성합니다.")
                    with LoadFile(self.srs_filename).readwrite() as srs_file:
                        srs_file.write("[-TRIM-][-SORT-]\n\n")
                        # TRIM:앞뒤공백 제거, SORT:긴 순서/알파벳 정렬, WORDWRAP:정확히 단어 단위일때만 치환
                orig_dictnames = list(orig_dictinfo.keys())
                trans_dictnames = list(trans_dictinfo.keys())
                for num in range(len(orig_dictinfo)):
                    try:
                        self.orig_dictname = orig_dictnames[num]
                        self.trans_dictname = trans_dictnames[num]
                    except IndexError as error:
                        self.srslog_file.write("{}에서 {} 발생.".format(orig_dictnames[num],error))
                        self.cantwrite_srs_count += 1
                        continue
                    if self.orig_dictname == 'ONLYONE': keyname = "단독파일"
                    else: keyname = DataFilter().sep_filename(self.orig_dictname)
                    if keyname.lower() != DataFilter().sep_filename(self.trans_dictname).lower():
                        self.trans_dictname = DataFilter(
                            ).search_filename_wordwrap(trans_dictnames,keyname.split())
                        if self.trans_dictname == None:
                            self.cantwrite_srs_count += 1
                            self.srslog_file.write("키워드: {} 불일치 존재.\n\n".format(keyname))
                            continue
                        self.srslog_file.write("{}번째부터 순서 불일치로 추가탐색 진행함\n\n.".format(num))
                    orig_valdict = orig_dictinfo.get(self.orig_dictname)
                    trans_valdict = trans_dictinfo.get(self.trans_dictname)
                    self.__SRS_multi_write(orig_valdict,trans_valdict,keyname)
                    # 이 단계에서 들어오는 valdict = {숫자, 데이터} 형식
            if self.cantwrite_srs_count != 0:
                print("{}쌍의 데이터가 정확히 작성되지 못했습니다. srsdebug.log를 확인해주세요.".format(
                                                                    self.cantwrite_srs_count))

    def __SRS_dict_type_check(self): #  데이터 입력과 유효체크 동시
        auth_switch = 0
        while auth_switch == 0: # 출력 가능한 데이터가 나올때까지 반복
            orig_data,trans_data = self.__multi_data_input()
            try:
                orig_vals = list(orig_data.values()) # dictinfo 결과물이라면 각 사전 데이터임.
                trans_vals = list(trans_data.values())
                if os.path.isfile(list(orig_data.keys())[0]) == True: # dictinfo 결과물인지 체크
                    # {파일명, csv딕셔너리 구조}
                    if isinstance(orig_vals[0],dict) == True and isinstance(
                                                trans_vals[0],dict) == True:
                        orig_dictinfo, trans_dictinfo = orig_data, trans_data
                        auth_switch = 1
                    # {파일명, erb리스트 구조}
                    # elif isinstance(orig_vals[0],list) == True and isinstance(
                    #                             trans_vals[0],list) == True:
                    #     auth_switch = 1
                    #     return orig_data, trans_data
                elif orig_vals == [] or trans_vals == []:
                    print("빈 데이터가 포함되어 있습니다.")
                    orig_dictinfo = None; trans_dictinfo = None
                else:
                    orig_dictinfo = {'ONLYONE':orig_data}
                    trans_dictinfo = {'ONLYONE':trans_data}
                    auth_switch = 1
            except:
                print("입력된 데이터가 딕셔너리형이 아니거나 빈 데이터입니다.")
                orig_dictinfo = None; trans_dictinfo = None
        return orig_dictinfo, trans_dictinfo

    def __SRS_multi_write(self,orig_dict,trans_dict,keyname):
        if orig_dict == None or trans_dict == None:
            print("SRS를 작성할 수 없습니다.")
            return 0
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


class ResultFunc:
    def make_result(self,target_name,target_data,result_type=0): # 0:txt, 1:erb, 2:srs
        resultdir_exist = DirCheck()
        resultdir_exist.run()
        if target_name == None and target_data == None:
            result_file = ExportData(resultdir_exist.dirname,target_name,target_data)
        else:
            dirname = resultdir_exist.dirname + target_name + '\\'
            sub_resultdir_exist = DirCheck()
            sub_resultdir_exist.run(dirname)
            result_file = ExportData(dirname,target_name,target_data)
        if result_type == 0:
            print("지정된 데이터의 TXT 파일화를 진행합니다.")
            result_file.to_TXT()
        elif result_type == 1:
            print("지정된 데이터의 ERB 파일화를 진행합니다.")
            result_file.to_TXT('erb')
        elif result_type == 2:
            print("csv 변수로 작성시 chara 폴더가 제외되어있어야 합니다.")
            print("작성 또는 수정할 srs 파일명을 입력해주세요.")
            srs_name = input("공란일 시 autobuild.simplesrs로 진행합니다. :")
            if bool(srs_name) == False: result_file.to_SRS()
            else: result_file.to_SRS(srs_name)
        if result_file.lazy_switch == 1:
            print("파일 처리를 진행하지 않았습니다.")
        else:
            print("처리가 완료되었습니다.")
        input("엔터를 눌러 계속...")