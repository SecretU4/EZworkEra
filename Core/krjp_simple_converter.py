# 한국/원판 간 구상 호환을 도와주는 툴

import pickle
import os
from customdb import InfoDict
from simple_util import BringFiles
from usefile import CustomInput, MenuPreset
from Ctrltool.erbcore import ERBRemodel, ERBVFinder
from Ctrltool.erhcore import HandleDIM, ERHFunc


class SaveSetting:
    def __init__(self):
        self.sav_name = "setting.sav"
        self.set_list = []
        self.sav_ver = 1.1

    def create(self):
        o_dir, *_ = CustomInput("원본 에라").input_option(0b001)
        o_encoding = MenuPreset().encode()
        t_dir, *_ = CustomInput("번역본 에라").input_option(0b001)
        t_encoding = MenuPreset().encode()
        f_csvinfo = BringFiles(o_dir).search_csvdict(o_encoding)
        t_csvinfo = BringFiles(t_dir).search_csvdict(t_encoding)
        self.set_list = [o_dir, t_dir, f_csvinfo, t_csvinfo, o_encoding, t_encoding]

    def save(self):
        if not os.path.isfile(self.sav_name):
            savfile = open(self.sav_name, "xb")
            pickle.dump((self.set_list, self.sav_ver), savfile, pickle.HIGHEST_PROTOCOL)
        else:
            print("설정 파일이 이미 존재하므로 저장하지 않습니다.")
            return None

    def load(self):
        if os.path.isfile(self.sav_name):
            self.savfile = open(self.sav_name, "rb")
            loaded = pickle.load(self.savfile)
            if isinstance(loaded, tuple):
                self.set_list, _ = loaded
            else:
                self.set_list = loaded
        elif [x for x in os.listdir("./") if x.endswith(".sav")]:
            print("설정 파일이 너무 많습니다. 하나만 남겨주세요.")
        else:
            print("설정 파일이 없습니다. 설정을 새롭게 작성합니다.")
            self.create()
        return self.set_list


class AnalyzeFiles:
    def __init__(self, bringfiles, encode_type):
        self.birngfiles = bringfiles
        self.encode_type = encode_type
        self.dim_dict = dict()

    def anal_erbs(self, double_csv_infodict=None, mod=0b111):
        """ERB 파일 분석 함수. double_csv_infodict은 (원본, 번역본) 형태의 튜플이어야 함.
        mod 설정정보
            bit 0 : 함수, bit 1 : CSV변수, bit 2: DIM변수
        """
        erb_files = self.birngfiles.search_filelist(".ERB")
        used_func_list = set(("LOCAL", "LOCALS"))
        def_func_list = set(("LOCAL", "LOCALS"))

        if mod & 0b010:
            if not double_csv_infodict:
                raise NotImplementedError("필요한 csvinfo 데이터가 입력되지 않았습니다.")
            try:
                from_csvinfo, to_csvinfo = double_csv_infodict
            except ValueError:
                print("올바르지 않은 자료형이 double_csv_infodict 인자로 들어왔습니다.")
                return False

            vfinder = ERBVFinder(from_csvinfo)
            csv_varlist = []
        if mod & 0b100:
            handle_dim = HandleDIM()

        for erbname in erb_files:
            with open(erbname, "r", encoding=self.encode_type) as erbfile:
                lines = erbfile.readlines()
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
                            used_func_list.add(funcname)
                    elif mod & 0b001 and head.startswith("@"):
                        funcname = head.replace("@", "").split("(")[0].split(",")[0]
                        def_func_list.add(funcname)
                if mod & 0b010: # CSV Vars
                    result = vfinder.find_csvfnc_line(line)
                    if result:
                        csv_varlist.extend(result)
                if mod & 0b100 and words[0].startswith("#DIM"): # DIM Vars
                    self.dim_dict.update(handle_dim.dim_search(line))  # TODO DIM 분석필요

        if mod & 0b010: # CSV Vars
            changed_csvvar = vfinder.change_var_index(csv_varlist, 1)
            changed_csvvar = DataFilter().dup_filter(changed_csvvar)
            used_csvvar, index_csvvar = vfinder.print_csvfnc(changed_csvvar, 0b1100)

        return used_func_list, used_csvvar, index_csvvar, self.dim_dict

    def anal_erhs(self):
        erh_files = self.birngfiles.search_filelist(".ERH")
        _, temp_dimdict = ERHFunc().analyze_erh(erh_files, self.encode_type)
        self.dim_dict.update(temp_dimdict)
        return temp_dimdict


class PrintERB:
    def __init__(self, dirname, encode_type, csv_infodict):
        self.erb_files = BringFiles(dirname).search_filelist(".ERB")
        self.encode_type = encode_type
        self.csv_infodict = csv_infodict

    def printing(self):
        result_infodict = InfoDict(1)
        for filename in self.erb_files:
            replaced_lines = ERBRemodel(
                filename, self.encode_type
                ).replace_csvvars(self.csv_infodict, 1)
            result_infodict.add_dict(filename, replaced_lines)
        return result_infodict

    def zname(self):  # TODO 추후 추가예정
        pass


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


def compare_csvvar(csv_dict, used_list, dim_dict=dict()):
    not_checked = used_list.copy()
    vfinder = ERBVFinder(csv_dict)
    csvname_dict = vfinder.csv_fnames
    extra_csvs = vfinder.extra_dict

    for var in used_list:
        is_dim = 0
        csvname, *vardata = var.split(":")
        var_context = vardata[-1]

        if csvname in list(extra_csvs.keys()):
            csvname = extra_csvs[csvname]

        if csvname in list(csvname_dict.keys()):
            csv_filename = csvname_dict[csvname]
            if dim_dict.get(var_context):  # dim_dict은 전역변수 정의 목록임. 명칭과 해당값 있음
                var_context = dim_dict[var_context][0]
                is_dim = 1
            if csv_dict.dict_main[csv_filename].get(var_context):
                not_checked.pop(not_checked.index(var))
            elif is_dim:
                vardata[-1] = var_context
                trans_var = csvname + ":" + ":".join(vardata)
                try:
                    not_checked.pop(not_checked.index(trans_var))
                except ValueError:
                    pass

    return not_checked


def wrapping(dirname, f_csvinfo, encode_type, t_csvinfo, target_dir):
    """simple_converter용 정리 함수
        Arguments
            dirname: 구상 출처 에라 위치
            f_csvinfo: 구상 출처 에라 CSV정보
            encode_type: 구상 출처 에라 인코딩 정보
            t_csvinfo: 이식 대상 에라 CSV정보
            target_dir: 이식할 구상 위치
    """
    # 주어진 데이터를 체크
    analyze = AnalyzeFiles(BringFiles(target_dir), encode_type)
    analyze.anal_erhs()
    used_funcs, used_csvvars, *compare_set = analyze.anal_erbs((f_csvinfo, t_csvinfo))

    index_csvvars = compare_csvvar(t_csvinfo, *compare_set)
    report = PrintReport()
    report.basic_info(target_dir, "외부함수 %d 개" % len(used_funcs), "미확인된 외부함수: ")
    report.listed_info(used_funcs)
    report.basic_info(
        "사용된 변수 %d 개\n누락 CSV변수: %d 개\n누락 목록: " % (len(used_csvvars), len(index_csvvars))
    )
    report.listed_info(index_csvvars)
    report.basic_info("\n" + "-" * 8)
    report.basic_info("이하 확인된 DIM 변수 초기값 목록: ")
    report.listed_info(compare_set[1])
    report.basic_info("\n" + "=" * 8)

    wrap_print = PrintERB(target_dir, encode_type, f_csvinfo)
    result_infodict = wrap_print.printing()
    for filename, erblines in result_infodict.dict_main.items():
        with open(filename, "w", encoding="utf-8-sig") as erb:
            erb.writelines(erblines)
    print(report.txtfile, "확인바람.")


# 이하 구동부
if __name__ == "__main__":
    print(
        "일어본/번역본 간 동일한 기능을 하는 ERB 이름이 (번역 등 이유로) 차이가 있는 경우,\n",
        "중복되는 기능을 하는 파일을 수동으로 처리해주셔야 합니다.\n",
        "해당 경우 누락된 함수에서 오류를 발생시킬 수 있습니다.\n\n",
    )
    config = SaveSetting()
    o_dir, t_dir, f_csvinfo, t_csvinfo, o_encod, t_encod = config.load()
    config.save()

    while True:
        print(
            "=" * 8,
            "\n한 번 실행한 적이 있는 경우, setting.sav 파일에 선택한 폴더, CSV 데이터 등이 저장됩니다.\n",
            "다른 폴더를 사용하거나 CSV 파일에 변동이 있었던 경우 해당 파일을 지우고 다시 구동해주세요.\n",
            "=" * 8,
            "\n[0] 일어본구상 번역본이식\n[1] 번역본구상 일어본이식\n",
        )
        choose = input("실행할 작업을 선택해주세요. : ")
        if choose == "0":
            chosen = [o_dir, f_csvinfo, o_encod, t_csvinfo]
        elif choose == "1":
            chosen = [t_dir, t_csvinfo, t_encod, f_csvinfo]
        else:
            print("올바른 입력이 아닙니다")
            continue
        print("이식할 구상이 있는 폴더를 입력하세요.")
        target_dir = input("* 에라 전체 폴더 선택시 문제가 발생할 수 있습니다.: ")
        wrapping(*chosen, target_dir)
        break
    input("아무 키나 눌러 종료...")
