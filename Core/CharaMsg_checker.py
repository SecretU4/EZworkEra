# 구상 diff 판별 툴

import os
from simple_util import BringFiles


def make_filedict(files):
    orig_dict = {}
    for filename in files:
        orig_dict[os.path.basename(filename)] = filename
    return orig_dict


orig_dirname = input("원본 디렉토리명: ")
trans_dirname = input("번역본 디렉토리명: ")
orig_files = BringFiles(orig_dirname).search_filelist(".ERB", ".ERH")
trans_files = BringFiles(trans_dirname).search_filelist(".ERB", ".ERH")

orig_filedict = make_filedict(orig_files)
trans_filedict = make_filedict(trans_files)

log_file = open("the_log.log", "w", encoding="utf-8-sig")
for filename in orig_filedict:
    try:
        real_diff = trans_filedict.pop(filename)
        with open(orig_filedict[filename], "r", encoding="utf-8-sig") as orig_file:
            orig_data = orig_file.read()
        with open(real_diff, "r", encoding="utf-8-sig") as trans_file:
            trans_data = trans_file.read()
        if not orig_data == trans_data:
            print(real_diff, "변경사항 확인요망\n", file=log_file)
    except:
        print(filename, "삭제된 파일인지 확인\n", file=log_file)
if trans_filedict:
    for key in trans_filedict:
        print(key, "추가된 파일인지 확인\n", file=log_file)
