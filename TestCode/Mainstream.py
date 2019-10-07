# EmuEra용 번역 파일 처리/합병 툴
# 사용되는 라이브러리
from Custom_Main import *
from Custom_CSV import CSVLoad
# from Custom_ERB import ERBLoad, ERBWrite
print("EZworkEra - Develop utility for EmuEra base game".center(20))
MainMenu1 = Main_Menu()
while True:
    MainMenu1.Run_MainMenu()
    # [1] CSV 파일의 처리
    if MainMenu1.MenuSelect == '1':
        print("CSV 파일 처리 유틸리티입니다.")
        DebugTXT = LoadFile('debug.txt','UTF-8').readwrite()
        CSV_User_input = Custom_input("CSV")
        Target_Dir_CSV = CSV_User_input.InputOption(1)
        Encode_Type = Encode().Encode_input()
        CSVFile_List = Find_File_in_Dir().FileList_Ext(Target_Dir_CSV,'.CSV')
        for filename in CSVFile_List:
            CSVOpenFile = CSVLoad(filename,Encode_Type)
            with CSVOpenFile.readonly() as LoadedCSV:
                for line in filename:
                    CSVOpenFile.CoreCSV(0,0)
            print('{0}{1}\n'.format(filename,CSVOpenFile.DataDic),file=DebugTXT)
        print("추출이 완료되었습니다.")
        MainMenu1.CSVMenu = 0
    MainMenu1.Run_MainMenu()
    # [2] ERB 파일의 처리
    if MainMenu1.MenuSelect == '2':
        print("미실장입니다.")
        MainMenu1.ERBMenu = 0
    MainMenu1.Run_MainMenu()
    # [3] ERH 파일의 처리
    if MainMenu1.MenuSelect == '3':
        print("미실장입니다")
        MainMenu1.ERHMenu = 0
    MainMenu1.Run_MainMenu()
    # [4] 프로그램 종료
    if MainMenu1.MenuSelect == '4':
        break
Common_Sent().EndComment()