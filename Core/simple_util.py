"""심플 모듈용 유틸리티 모음"""

from usefile import FileFilter
from Ctrltool.csvcore import CSVFunc


class BringFiles:
    def __init__(self, dirname):
        self.dirname = dirname

    def search_csvdict(self, encode_type):
        csv_filelist = FileFilter(1).files_ext(self.dirname, ".CSV")
        CSVinfodict = CSVFunc().import_all_CSV(0b10, csv_filelist, encode_type)
        return CSVinfodict

    def search_filelist(self, *ext, opt=1):
        result = []
        for ex in ext:
            if not ex.startswith("."):
                ex = "." + ex
            result.extend(FileFilter(opt).files_ext(self.dirname, ex))
        return result
