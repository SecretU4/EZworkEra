# CSV 기능 관련 모듈
from Custom_Main import LoadFile, DataFilter
import csv
class CSVLoad(LoadFile):
    def CSVRun(self):
        self.CSVRead = csv.reader(self.readonly())
    def CoreCSV(self, Select_dataNum, Filter_info):
        self.CSVRun()
        self.DataDic = {}
        for row_list in self.CSVRead:
            First_data = None
            Second_data = None
            try:
                First_data = str(row_list[0]).strip()
                Second_data = str(row_list[1]).strip()
                if Select_dataNum == 1:
                    Selected_dataset = First_data
                    Another_dataset = Second_data
                elif Select_dataNum == 2:
                    Selected_dataset = Second_data
                    Another_dataset = First_data
            except IndexError: continue
            if Select_dataNum == 0:
                self.DataDic[First_data]=Second_data
            elif Selected_dataset == Filter_info:
                self.DataDic[Selected_dataset]=Another_dataset
    def InfoCSV(self):
        self.CSVRun()
        InfoDATA_list = []
        for row_list in self.CSVRead:
            try:
                DATA_1 = str(row_list[0])
                DATA_2 = str(row_list[1])
            except IndexError: continue
            InfoDATA_list.append(DATA_1)
            InfoDATA_list.append(DATA_2)
        InfoCSV_DATA = DataFilter.Dup_Filter(InfoDATA_list)
        return InfoCSV_DATA