"""ERB 내 DIM 기능 작성 시연용 모듈"""

import re
from customdb import FuncInfo
from usefile import CustomInput, MenuPreset
from Ctrltool.erbcore import ERBLoad
from Ctrltool.erhcore import HandleDIM


search_str = re.compile('"([^"]+)"')


def erb_translate_check(erb_files=None, encode_type=None):
    if not erb_files or not encode_type:
        erb_files, encode_type = CustomInput("ERB").get_filelist()
    func_dict = FuncInfo()

    for erb_file in erb_files:
        func_name = "N/A"
        total_strs = []

        loaded_erb = ERBLoad(erb_file, encode_type)
        bulklines = loaded_erb.make_bulklines()
        for line in bulklines:
            line = line.strip()
            if line.startswith("@"):  # 함수문 시작지점
                func_dict.add_dict(func_name, total_strs, erb_file)
                func_name = line.split("(")[0]
                total_strs = []
            #     dim_dict = dict()
            # elif line.startswith("#DIM"):
            #     dim_dict.update(HandleDIM(dim_dict).dim_search(line))
            elif line.find('"') > -1:
                str_list = search_str.findall(line)
                for string in str_list:
                    if string.find("/") > -1:
                        # string_list = string.split("/")
                        # total_strs.extend(string_list)
                        total_strs.append(string)
                    else:
                        total_strs.append(string)
            else:
                pass
        func_dict.add_dict(func_name, total_strs, erb_file)  # 마지막 함수용
    return func_dict


with open("dimtest.log", "w", encoding="UTF-8") as log:
    funcinfo = erb_translate_check()
    for key, value in funcinfo.func_dict.items():
        if isinstance(value, dict):
            org = list(value.items())
        elif isinstance(value, list):
            org = value
        text = "%s\n" % key + ", ".join(org) + "\n\n"
        print(text, file=log)
    MenuPreset().shall_save_data(funcinfo, "FuncInfo")

