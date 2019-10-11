# EmuEra용 번역 파일 처리/합병 툴
# 사용되는 라이브러리
from Custom_Main import Common_Sent, Menu
from Custom_CSV import CSVLoad, CSV_FuncModule
# from Custom_ERB import ERBLoad, ERBWrite
Menu_Main_Dict = {0:'CSV 파일 처리',1:'ERB 파일 처리 (미실장)',2:'ERH 파일 처리 (미실장)',3:'프로그램 종료'}
MainMenu = Menu(Menu_Main_Dict)
MainMenu.Title("EZworkEra - Develop utility for EmuEra base game")
while True:
    print("작업 후 버튼을 눌러 프로그램을 종료하셔야 작업파일이 손실되지 않습니다.")
    Common_Sent.PrintLine
    MainMenu.Run_Menu()
# [1] CSV 파일의 처리
    if MainMenu.MenuSelect == 0:
        print("CSV 파일 처리 유틸리티입니다.")
        CSV_FuncModule().Import_All_CSV()
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