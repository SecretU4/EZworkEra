# EmuEra용 번역 파일 처리/합병 툴
# 사용되는 라이브러리
from customcore import CommonSent, Menu
from custom_csv import CSVFunc
# from Custom_ERB import ERBLoad, ERBWrite
menu_dict_main = {0: 'CSV 파일 처리', 1: 'ERB 파일 처리 (미실장)',
                2: 'ERH 파일 처리 (미실장)', 3: '프로그램 종료'}
MainMenu = Menu(menu_dict_main)
MainMenu.title("EZworkEra - Develop utility for EmuEra base game")
while True:
    print("작업 후 버튼을 눌러 프로그램을 종료하셔야 작업파일이 손실되지 않습니다.")
    CommonSent.print_line()
    MainMenu.run_menu()
# [1] CSV 파일의 처리
    if MainMenu.selected_num == 0:
        print("CSV 파일 처리 유틸리티입니다.")
        CSVFunc().import_all_CSV()
        MainMenu.selected_num = 0
# [2] ERB 파일의 처리
    elif MainMenu.selected_num == 1:
        print("미실장입니다.")
        MainMenu.selected_num = 0
# [3] ERH 파일의 처리
    elif MainMenu.selected_num == 2:
        print("미실장입니다")
        MainMenu.selected_num = 0
# [4] 프로그램 종료
    elif MainMenu.selected_num == 3:
        break
CommonSent.end_comment()
