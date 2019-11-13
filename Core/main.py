# EmuEra용 번역 파일 처리/합병 툴
# 사용되는 라이브러리
import os
from util import CommonSent, Menu, MenuPreset
from csvcore import CSVFunc
from erbcore import ERBFunc
from result import ResultFunc
menu_dict_main = {
    0: 'CSV 파일 처리', 1: 'ERB 파일 처리',
    2: 'ERH 파일 처리 (미실장)', 3:'결과물 제어',
    4: '프로그램 종료'}
menu_main = Menu(menu_dict_main)
menu_main.title("EZworkEra - Develop utility for EmuEra base game")
last_work = None; last_work_name = None
while True:
    print("작업 후 버튼을 눌러 프로그램을 종료하셔야 작업파일이 손실되지 않습니다.")
    CommonSent.print_line()
    menu_main.run_menu()
# [0] CSV 파일의 처리
    if menu_main.selected_menu == 'CSV 파일 처리':
        CommonSent.print_line()
        menu_dict_csv = {0: 'CSV 변수 목록 추출',1: '이전으로'}
        menu_csv = Menu(menu_dict_csv)
        menu_csv.title("CSV 파일 처리 유틸리티입니다.")
        menu_csv.run_menu()
        if menu_csv.selected_num == 0:
            menu_dict_import_all_csv = {0: '모두',1:'CHARA제외',
                2:'CHARA만',3:'SRS 최적화-이름',4:'SRS 최적화-변수',5:'처음으로'}
            menu_import_all_csv = Menu(menu_dict_import_all_csv)
            menu_import_all_csv.title("추출할 CSV의 종류를 선택하세요.")
            menu_import_all_csv.run_menu()
            if menu_import_all_csv.selected_num != 5: # csv 변수추출 중 처음으로가 아님
                import_all_csv_dict = CSVFunc().import_all_CSV(menu_import_all_csv.selected_num)
                MenuPreset().shall_save_data(import_all_csv_dict.dict_info,'dict')
                last_work = import_all_csv_dict.dict_info # 마지막 작업 저장
        if menu_csv.selected_menu != '이전으로':
            last_work_name = menu_csv.selected_menu # 마지막 작업 명칭 저장
# [1] ERB 파일의 처리
    elif menu_main.selected_menu == 'ERB 파일 처리':
        print("ERB 파일 처리 유틸리티입니다. 현재 TW 파일 이외의 구동을 보장하지 않습니다.")
        menu_dict_erb = {0: '사용된 CSV 변수 추출', 1: '구상추출', 2: '이전으로'}
        menu_erb = Menu(menu_dict_erb)
        menu_erb.run_menu()
        if menu_erb.selected_num == 0:
            ERBFunc().search_csv_var() # result 모듈 적용 예정
        elif menu_erb.selected_num == 1:
            ERBFunc().extract_printfunc() # result 모듈 적용 예정
# [2] ERH 파일의 처리
    elif  menu_main.selected_menu == 'ERH 파일 처리 (미실장)':
        print("미실장입니다")
# [3] 결과물 제어
    elif menu_main.selected_menu == '결과물 제어':
        menu_dict_result = {0: '결과물 TXT화',1: '결과물 SRS화',2: '이전으로'}
        menu_result = Menu(menu_dict_result)
        menu_result.title("추출 결과물에 대한 제어 메뉴입니다.")
        menu_result.run_menu()
        if menu_result.selected_num == 0:
            ResultFunc().make_result(last_work_name,last_work)
        elif menu_result.selected_menu == '결과물 SRS화':
            ResultFunc().make_result(last_work_name,last_work,2)
# [4] 프로그램 종료
    elif menu_dict_main[menu_main.selected_num] == '프로그램 종료':
        break
CommonSent.end_comment()
