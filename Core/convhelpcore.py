# compact version of convert_helper

import chardet
import os
import time
from PIL import Image

version = "v1.4.1c"
encode_dict = {"Shift-JIS": "cp932", "UTF-8 with BOM": "utf-8-sig",
    "Korean-Windows": "cp949", "UTF-16 LE":"utf-16-le"}

def result_maker(filename, dir_from):
    filename = "Result" + filename.replace(dir_from, "")
    result_dir = os.path.dirname(filename)
    if not os.path.isdir(result_dir):
        dir_names = result_dir.split("\\")
        for depth in range(len(dir_names)):
            dir_make = "\\".join(dir_names[: depth + 1])
            if os.path.isdir(dir_make):
                continue
            os.mkdir(dir_make)
    return filename

def files_ext(dir_target, ext_target):
    #from FileFilter @usefile.py
    ext_target = ext_target.upper()
    result = []
    for (path, _, files) in os.walk(dir_target):
        for filename in files:
            file_type = os.path.splitext(filename)[-1].upper()
            if file_type == ext_target:
                result.append("{0}\\{1}".format(path, filename))
    return result

class ImageConvert:
    """image format converter"""
    def __init__(self, file_path, opt_array=[0, 0], dir_from=None):
        self.filename, _ = os.path.splitext(file_path)
        self.file_path = file_path
        img = Image.open(file_path)
        self.img_rgb = img.convert("RGB")
        if img.format in ("GIF", "PNG", "WEBP"): # format support Alpha
            self.opened_image = img.convert("RGBA")
        else:
            self.opened_image = self.img_rgb
        self.make_backup = opt_array[1]
        self.dir_from = dir_from

    def convert_image(self, dest_fmt):
        if self.make_backup and self.dir_from:
            self.filename = result_maker(self.filename, self.dir_from)
        else:
            if os.path.isfile(self.file_path):
                os.remove(self.file_path)
            else:
                print("ERROR - NOFILE to DELETE")
        try:
            self.opened_image.save(self.filename + "." + dest_fmt, dest_fmt)
        except OSError: # format not support Alpha
            self.img_rgb.save(self.filename + "." + dest_fmt, dest_fmt)


class TXTConverter:
    '''txt encoding convert with change img_ext related context'''
    def __init__(
        self, filename, target_encode, orig_imgext="", to_imgext="", opt_array=[0, 0], dir_from=None
    ):
        self.filename = filename
        self.opened_file = open(filename, "rb")
        self.encode_to = target_encode
        self.orig_imgext = orig_imgext
        self.to_imgext = to_imgext
        self.change_ext_inTXT = opt_array[0]
        self.get_backup = opt_array[1]
        self.dir_from = dir_from

    def encoding_check(self):
        detect_result = chardet.detect(self.opened_file.read())
        return detect_result["encoding"]

    def change_encoding(self, encode_to):
        bulk_data = None
        while bulk_data == None:
            for encode in encode_dict.values():
                bulk_data = self.try_open(encode)
                if isinstance(bulk_data, str):
                    break
            if bulk_data == None:
                encode = self.encoding_check()
                bulk_data = self.try_open(encode)
        if self.orig_imgext and self.change_ext_inTXT:
            bulk_data = bulk_data.replace(self.orig_imgext, self.to_imgext)

        if self.get_backup and self.dir_from:
            dest_filename = result_maker(self.filename, self.dir_from)
        else:
            dest_filename = self.filename
        with open(dest_filename, "w", encoding=encode_to) as dest:
            dest.write(bulk_data)

    def try_open(self, encoding):
        try:
            with open(self.filename, "r", encoding=encoding) as origin:
                bulk_data = origin.read()
            return bulk_data
        except UnicodeDecodeError:
            return None

    def run(self):
        self.change_encoding(self.encode_to)

if __name__ == "__main__":
    print("current-version: " + version)
    cur_path = "resources"
    if not os.path.isdir(cur_path):
        print("Please put this file in parent directory of 'resources'")
        time.sleep(5)
    else:
        for img_file in files_ext(cur_path, 'webp'):
            ImageConvert(img_file).convert_image('png')
        for csv_file in files_ext(cur_path, 'csv'):
            TXTConverter(csv_file, 'utf-8-sig', 'webp', 'png', [True, False]).run()
        print('Done!')
        time.sleep(3)