# ERB 관련 모듈
from customcore import LoadFile
from custom_csv import CSVLoad


class ERBLoad(LoadFile):
    def make_erb_list(self):
        with self.readonly() as erb_origin:
            self.erb_context_list = []
            self.erb_context_list.append(erb_origin.readline())
            return self.erb_context_list

    def search_line(self,Target):
        self.make_erb_list()
        self.targeted_list = []
        for line in self.erb_context_list:
            if Target in line:
                self.targeted_list.append(line)
        return self.targeted_list

    def search_func(self,Func):
        self.make_erb_list()
        func_list = CSVLoad('CSVfnclist.csv','').info_data_csv()
        if Func in func_list:
            pass


class ERBWrite(LoadFile):
    def _export_erb(self):
        self.erb_exporting = LoadFile('trans_{0}.erb'.format(
            self.NameDir),self.EncodType)

    def trans_erb(self):
        self._export_erb()
        with self.readonly() as txt_origin:
            txt_text_list = []
            txt_context = txt_origin.readline()
            txt_text_list.append(txt_context)
        for line in txt_text_list:
            pass
        self.erb_exporting.close()