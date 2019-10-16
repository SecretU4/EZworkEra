# EmuEra용 번역 파일 처리/합병 툴
# 사용되는 라이브러리
from customcore import CommonSent, Menu
from custom_csv import CSVFunc
from custom_erb import ERBFunc
# from Custom_ERB import ERBLoad, ERBWrite
menu_dict_main = {0: 'CSV 파일 처리', 1: 'ERB 파일 처리 (미실장)',
                2: 'ERH 파일 처리 (미실장)', 3: '프로그램 종료'}
menu_main = Menu(menu_dict_main)
menu_main.title("EZworkEra - Develop utility for EmuEra base game")
while True:
    print("작업 후 버튼을 눌러 프로그램을 종료하셔야 작업파일이 손실되지 않습니다.")
    CommonSent.print_line()
    menu_main.run_menu()
# [1] CSV 파일의 처리
    if menu_main.selected_num == 0:
        print("CSV 파일 처리 유틸리티입니다.")
        CommonSent.print_line()
        menu_dict_csv = {0: 'CSV 변수 목록 추출'}
        menu_csv = Menu(menu_dict_csv)
        menu_csv.run_menu()
        if menu_csv.selected_num == 0:
            CSVFunc().import_all_CSV()
        del menu_csv.selected_num
        del menu_main.selected_num
# [2] ERB 파일의 처리
    elif menu_main.selected_num == 1:
        print("현재 기능 작성중입니다. 껍데기 뿐입니다.")
        menu_dict_erb = {0: '사용된 CSV 변수 추출', 1: '구상추출'}
        menu_erb = Menu(menu_dict_erb)
        menu_erb.run_menu()
        if menu_erb.selected_num == 0:
            ERBFunc().search_csv_var()
        elif menu_erb.selected_num == 1:
            ERBFunc().extract_printfunc()
        del menu_erb.selected_num
        del menu_main.selected_num
# [3] ERH 파일의 처리
    elif menu_main.selected_num == 2:
        print("미실장입니다")
        del menu_main.selected_num
# [4] 프로그램 종료
    elif menu_main.selected_num == 3:
        break
CommonSent.end_comment()
