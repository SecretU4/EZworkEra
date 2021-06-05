# 한국/원판 간 구상 호환을 도와주는 툴

import pickle
import os
from customdb import FuncInfo, InfoDict
from simple_util import BringFiles
from usefile import CustomInput, MenuPreset
from util import DataFilter
from Ctrltool.erbcore import ERBRemodel, ERBVFinder
from Ctrltool.erhcore import HandleDIM, ERHFunc
from Ctrltool.srshandler import SRSFunc


class SaveSetting:
    def __init__(self):
        self.sav_name = "setting.sav"
        self.set_dict = {"sav_ver":1.1}

    def create(self):
        dir_ori, *_ = CustomInput("원본 에라").input_option(0b001)
        enc_ori:str = MenuPreset().encode()
        self.set_dict["csv_A"] = BringFiles(dir_ori).search_csvdict(enc_ori)
        self.set_dict["dir_A"] = dir_ori
        self.set_dict["enc_A"] = enc_ori
        dir_tns, *_ = CustomInput("번역본 에라").input_option(0b001)
        enc_tns:str = MenuPreset().encode()
        self.set_dict["csv_B"] = BringFiles(dir_tns).search_csvdict(enc_tns)
        self.set_dict["dir_B"] = dir_tns
        self.set_dict["enc_B"] = enc_tns
        return self.set_dict

    def save(self, data):
        if not os.path.isfile(self.sav_name):
            savfile = open(self.sav_name, "xb")
            pickle.dump(data, savfile, pickle.HIGHEST_PROTOCOL)
        else:
            print("설정 파일이 이미 존재하므로 저장하지 않습니다.")
        return data

    def load(self) -> dict:
        if os.path.isfile(self.sav_name):
            self.savfile = open(self.sav_name, "rb")
            data = pickle.load(self.savfile)
        elif [x for x in os.listdir("./") if x.endswith(".sav")]:
            raise FileExistsError("설정 파일이 너무 많습니다. 하나만 남겨주세요.")
        else:
            print("설정 파일이 없습니다. 설정을 새롭게 작성합니다.")
            data = self.create()
        
        return self.save(data)


class AnalyzeFiles:
    def __init__(self, bringfiles:BringFiles, encode_type:str):
        self.bring = bringfiles
        self.encode_type = encode_type
        self.dim_dict: dict[str, list[str]] = dict()

    def anal_erbs(self, mod: int = 0b111):
        """ERB 파일 분석 함수.

        mod 설정정보
            bit 0 : 함수, bit 1 : CSV변수, bit 2: DIM변수
        """
        self.erb_infdict = InfoDict(1)
        for erb in self.bring.search_filelist(".ERB"):
            with open(erb, "r", encoding=self.encode_type) as erbfile:
                self.erb_infdict.add_dict(erb, erbfile.readlines())
        self.anal_erhs()

        if mod & 0b001: # Function 처리
            def_funcinfo = FuncInfo()
            use_funcinfo = FuncInfo()
            mis_funcs = []
        if mod & 0b010: # CSV Var 처리
            csv_varlist = []
        if mod & 0b100: # DIM Var 처리
            handle_dim = HandleDIM()

        for erbname, lines in self.erb_infdict.dict_main.items():
            # line당 여건 체크
            for line in lines:
                line.strip()
                if line.startswith(";"): # Comment
                    continue
                words = line.split()
                if not words:
                    continue
                if mod & 0b001: # Function
                    head = words[0]
                    if mod & 0b001 and head in ("TRYCALLFORM", "TRYCCALLFORM", "TRYCALL", "CALLFORM", "CALLF", "CALL"):
                        words.pop(0)
                        funcname = " ".join(words).split("(")[0]
                        try:
                            int(funcname)
                        except ValueError:
                            use_funcinfo.add_dict(funcname, [funcname,], erbname)
                    elif mod & 0b001 and head.startswith("@"):
                        funcname = head.replace("@", "").split("(")[0].split(",")[0]
                        def_funcinfo.add_dict(funcname, [funcname,], erbname)
                if mod & 0b010: # CSV Vars
                    result = self.vfinder.find_csvfnc_line(line)
                    if result:
                        csv_varlist.extend(result)
                if mod & 0b100 and words[0].startswith("#DIM"): # DIM Vars
                    self.dim_dict.update(handle_dim.dim_search(line))  # TODO DIM 분석필요

        # 결과물 처리 부분
        used_csvvar = []
        index_csvvar = []
        if mod & 0b001: # Function
            for used_func in use_funcinfo.func_dict:
                if not def_funcinfo.func_dict.get(used_func):
                    mis_funcs.append(used_func)
        if mod & 0b010: # CSV Vars
            changed_csvvar = self.vfinder.change_var_index(csv_varlist, 1)
            changed_csvvar = DataFilter().dup_filter(changed_csvvar)
            used_csvvar, index_csvvar = self.vfinder.print_csvfnc(changed_csvvar, 0b1100)
            index_csvvar = self.compare_csvvar(index_csvvar)

        return mis_funcs, used_csvvar, index_csvvar

    def anal_erhs(self) -> dict[str, list[str]]:
        """분석할 ERB의 기반 ERH를 분석해 그 결과값을 dict형태로 반환함"""
        erh_files = self.bring.search_filelist(".ERH")
        if not erh_files: # 주어진 구상 폴더 내에 ERH 파일이 없음
            return {}
        _, temp_dimdict = ERHFunc().analyze_erh(erh_files, self.encode_type)
        self.dim_dict.update(temp_dimdict)
        return temp_dimdict
    
    def anal_csvs(self, f_csvinfo: InfoDict, t_csvinfo: InfoDict) -> dict:
        self.vfinder = ERBVFinder(f_csvinfo)
        self.t_vfinder = ERBVFinder(t_csvinfo)
        srs_dict, *_ = SRSFunc().build_srsdict(f_csvinfo, t_csvinfo)
        return srs_dict

    def compare_csvvar(self, used_list: list[str]):
        """index 기반 사용 변수 list를 받아 처리되지 않은 list 반환"""
        not_checked = used_list.copy()

        for var in used_list:
            is_dim = False
            csvname, *vardata = var.split(":")
            var_context = vardata[-1]

            if self.t_vfinder.extra_dict.get(csvname): # csvname != 일반적 filename
                csvname: str = self.t_vfinder.extra_dict[csvname]

            csv_filename: str = self.t_vfinder.csv_fnames.get(csvname)
            if csv_filename:
                if self.dim_dict.get(var_context):  # dim_dict 에서 찾을 수 있는 var_context인 경우
                    var_context = self.dim_dict[var_context][0] # 일단 1차원만 상정
                    is_dim = True

                if self.t_vfinder.csv_infodict.dict_main[csv_filename].get(var_context): # 해당 var_context가 목록에 존재하는 경우
                    trans_var = var
                elif is_dim:
                    vardata[-1] = var_context
                    trans_var = csvname + ":" + ":".join(vardata)
                else:
                    continue

                try:
                    not_checked.pop(not_checked.index(trans_var))
                except ValueError:
                    pass

        return not_checked


class PrintERB:
    def __init__(self, erb_info:InfoDict, encode_type:str, csv_info:InfoDict):
        self.erb_info = erb_info
        self.encode_type = encode_type
        self.csv_infodict = csv_info

    def printing(self, srs_dict:dict = dict()):
        result_infodict = InfoDict(1)
        for filename, lines in self.erb_info.dict_main.items():
            replaced_lines = ERBRemodel(lines).replace_csvvars(self.csv_infodict, 1, srs_dict)
            result_infodict.add_dict(filename, replaced_lines)
        return result_infodict


class PrintReport:
    def __init__(self, name="report.txt"):
        self.txtfile = name

    def basic_info(self, *info):
        with open(self.txtfile, "a", encoding="UTF-8") as opened:
            for inf in info:
                opened.write(str(inf) + "\n")

    def listed_info(self, info):
        with open(self.txtfile, "a", encoding="UTF-8") as opened:
            if isinstance(info, list) or isinstance(info, set) or isinstance(info, tuple):
                result = "\n".join(info)
            elif isinstance(info, dict):
                final_list = list(map(lambda x: "{}:{}".format(*x), info.items()))
                result = "dict 데이터 \n" + "\n".join(final_list)
            opened.write(result + "\n")


def wrapping(set_dict:dict, tag_no:int, target_dir:str):
    """simple_converter용 정리 함수
        Arguments
            f_csvinfo: 구상 출처 에라 CSV정보
            encode_type: 구상 출처 에라 인코딩 정보
            t_csvinfo: 이식 대상 에라 CSV정보
            target_dir: 이식할 구상 위치
    """
    # 주어진 데이터를 체크
    tag_dict = {0:"A", 1:"B", "A":"B", "B":"A"}
    from_tag = tag_dict.get(tag_no)
    if not from_tag:
        NotImplementedError("잘못된 태그: {}".format(tag_no))

    analyze = AnalyzeFiles(BringFiles(target_dir), set_dict["enc_"+from_tag])
    srsdict = analyze.anal_csvs(set_dict["csv_"+from_tag], set_dict["csv_"+tag_dict[from_tag]])
    miss_funcs, used_csvvars, index_csvvars = analyze.anal_erbs()

    report = PrintReport()
    report.basic_info(target_dir, "외부함수 %d 개" % len(miss_funcs), "미확인된 외부함수: ")
    report.listed_info(miss_funcs)
    report.basic_info(
        "사용된 변수 %d 개\n누락 CSV변수: %d 개\n누락 목록: " % (len(used_csvvars), len(index_csvvars))
    )
    report.listed_info(index_csvvars)
    report.basic_info("\n" + "-" * 8)
    report.basic_info("이하 확인된 DIM 변수 초기값 목록: ")
    report.listed_info(analyze.dim_dict)
    report.basic_info("\n" + "=" * 8)

    wrap_print = PrintERB(analyze.erb_infdict, set_dict["enc_"+from_tag], set_dict["csv_"+from_tag])
    result_infodict = wrap_print.printing(srsdict)
    for filename, erblines in result_infodict.dict_main.items():
        name_words = filename.split(".")
        name_words[-2] += "_conv"
        filename = ".".join(name_words)
        with open(filename, "w", encoding="utf-8-sig") as erb:
            erb.writelines(erblines)
    print(report.txtfile, "확인바람.")


# 이하 구동부
if __name__ == "__main__":
    version_str = "v2.0"
    print(
        "=" * 8,
        "일어본/번역본 간 동일한 기능을 하는 ERB 이름이 (번역 등 이유로) 차이가 있는 경우,",
        "중복되는 기능을 하는 파일을 수동으로 처리해주셔야 합니다.",
        "해당 경우 누락된 함수에서 오류를 발생시킬 수 있습니다.",
        "현재 버전: " + version_str,
        "=" * 8, sep="\n"
    )
    config = SaveSetting()
    set_dict = config.load()

    while True:
        print(
            "=" * 8,
            "\n한 번 실행한 적이 있는 경우, setting.sav 파일에 선택한 폴더, CSV 데이터 등이 저장됩니다.\n",
            "다른 폴더를 사용하거나 CSV 파일에 변동이 있었던 경우 해당 파일을 지우고 다시 구동해주세요.\n",
            "=" * 8,
            "\n[0] 일어본구상 번역본이식\n[1] 번역본구상 일어본이식\n",
        )
        choose = input("실행할 작업을 선택해주세요. : ")
        if choose not in ("0", "1"):
            print("올바른 입력이 아닙니다")
            continue
        choose = int(choose)
        break
    print("이식할 구상이 있는 폴더를 입력하세요.")
    target_dir = input("* 에라 전체 폴더 선택시 문제가 발생할 수 있습니다.: ")
    wrapping(set_dict, choose, target_dir)
    input("아무 키나 눌러 종료...")
