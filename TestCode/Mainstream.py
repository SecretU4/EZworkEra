# EmuEra용 번역 파일 처리/합병 툴
# 사용되는 라이브러리
from Custom_Main import Common_Sent, Menu, Menu_Preset, Custom_input, LoadFile, Find_File_in_Dir, DataFilter
from Custom_CSV import CSVLoad
# from Custom_ERB import ERBLoad, ERBWrite
Menu_Main_Dict = {0:'CSV 파일 처리',1:'ERB 파일 처리 (미실장)',2:'ERH 파일 처리 (미실장)',3:'프로그램 종료'}
MainMenu = Menu(Menu_Main_Dict)
MainMenu.Title("EZworkEra - Develop utility for EmuEra base game")
while True:
    MainMenu.Run_Menu()
    # [1] CSV 파일의 처리
    if MainMenu.MenuSelect == 0:
        print("CSV 파일 처리 유틸리티입니다.")
        DebugLog = LoadFile('debuglog.txt','UTF-8').readwrite()
        DebugLog.write("오류코드 0xef는 UTF-8-sig, 다른 경우 cp932(일본어),cp949(한국어)로 시도하세요.\n")
        DebugTXT = LoadFile('debug.txt','UTF-8').readwrite()
        CSV_User_input = Custom_input("CSV")
        Target_Dir_CSV = CSV_User_input.InputOption(1)
        Encode_Type = Menu_Preset().Encode()
        CSVFile_List = Find_File_in_Dir().FileList_Ext(Target_Dir_CSV,'.CSV')
        for filename in CSVFile_List:
            CSVOpenFile = CSVLoad(filename,Encode_Type)
            with CSVOpenFile.readonly() as LoadedCSV:
                try:
                    CSVOpenFile.CoreCSV(0,0)
                except UnicodeDecodeError as UniDecode:
                    print("{}에서 {} 발생\n".format(filename,UniDecode),file=DebugLog)
            CSVOpenFile.DataDic = DataFilter().EraseQuote(CSVOpenFile.DataDic,';')
            print('{0}\n{1}\n'.format(filename,CSVOpenFile.DataDic),file=DebugTXT)
        DebugTXT.close
        Common_Sent.ExtractFinish()
        MainMenu.MenuSelect = 0
    # [2] ERB 파일의 처리
    elif MainMenu.MenuSelect == 1:
        print("미실장입니다.")
        MainMenu.MenuSelect = 0
    # [3] ERH 파일의 처리
    elif MainMenu.MenuSelect == 2:
        print("미실장입니다")
        MainMenu.MenuSelect = 0
    # [4] 프로그램 종료
    elif MainMenu.MenuSelect == 3:
        break
Common_Sent.EndComment()