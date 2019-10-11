# CSV 기능 관련 모듈
from Custom_Main import LoadFile, DataFilter, Common_Sent, Menu, Menu_Preset, Custom_input, LoadFile, Find_File_in_Dir
import csv
class CSVLoad(LoadFile):
    def CSVRun(self):
        self.CSVRead = csv.reader(self.readonly())
    def CoreCSV(self, Select_dataNum, Filter_info):
        self.CSVRun()
        self.DataDic = {}
        for row_list in self.CSVRead:
            try:
                First_data = str(row_list[0]).strip()
                Second_data = str(row_list[1]).strip()
                if Select_dataNum == 0:
                    self.DataDic[First_data]=Second_data
                    continue
                elif Select_dataNum == 1:
                    Selected_dataset = First_data
                    Another_dataset = Second_data
                elif Select_dataNum == 2:
                    Selected_dataset = Second_data
                    Another_dataset = First_data
            except IndexError: continue
            if Selected_dataset == Filter_info:
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
        InfoCSV_DATA = DataFilter().Dup_Filter(InfoDATA_list)
        return InfoCSV_DATA
class CSV_FuncModule:
    def Import_All_CSV(self):
        print("추출을 시작합니다.")
        DebugTXT = LoadFile('debug.txt','UTF-8').readwrite()
        DebugLog = LoadFile('debuglog.txt','UTF-8').readwrite()
        DebugLog.write("오류코드 0xef는 UTF-8-sig, 다른 경우 cp932(일본어),cp949(한국어)로 시도하세요.\n")
        ErrorCheck, FileCount = 0,0
        CSV_User_input = Custom_input("CSV")
        Target_Dir_CSV = CSV_User_input.InputOption(1)
        Encode_Type = Menu_Preset().Encode()
        CSVFile_List = Find_File_in_Dir().FileList_Ext(Target_Dir_CSV,'.CSV')
        for filename in CSVFile_List:
            CSVOpenFile = CSVLoad(filename,Encode_Type)
            with CSVOpenFile.readonly():
                try:
                    CSVOpenFile.CoreCSV(0,0)
                except UnicodeDecodeError as UniDecode:
                    print("{}에서 {} 발생\n".format(filename,UniDecode),file=DebugLog)
                    ErrorCheck += 1
            CSVOpenFile.DataDic = DataFilter().EraseQuote(CSVOpenFile.DataDic,';')
            print('{0}\n{1}\n'.format(filename,CSVOpenFile.DataDic),file=DebugTXT)
            FileCount += 1
        if ErrorCheck != 0:
            print("{}건 추출 도중 {}건의 인코딩 오류가 발생했습니다. debuglog.txt를 확인해주세요.".format(FileCount,ErrorCheck))
        else:
            print("{}건이 추출되었습니다.".format(FileCount))
            DebugLog.write("오류가 발생하지 않았거나 덮어씌워졌습니다.")
        DebugTXT.close
        DebugLog.close
        Common_Sent.ExtractFinish()