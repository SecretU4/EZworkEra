# EmuEra용 번역 파일 처리/합병 툴
# 사용되는 라이브러리
from util import CommonSent
from Ctrltool import CSVFunc, ERBFunc, ResultFunc
from usefile import MenuPreset
from System.interface import Menu

menu_dict_main = {
    0: 'CSV 파일 처리', 1: 'ERB 파일 처리',
    2: 'ERH 파일 처리 (미실장)', 3:'결과물 제어',
    4: '프로그램 정보', 5: '프로그램 종료'}
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
        menu_dict_csv = {0: 'CSV 변수 목록 추출',1: 'CSV 변수 목록 추출(SRS 최적화)',
        2: 'CSV 변수 명칭 사전',3: '이전으로'}
        menu_csv = Menu(menu_dict_csv)
        menu_csv.title("CSV 파일 처리 유틸리티입니다.")
        menu_csv.run_menu()
        if menu_csv.selected_num == 0:
            menu_dict_import_all_csv = {0: '모두',1:'CHARA 제외',
                2:'문자/숫자 변환',3:'처음으로'}
            menu_import_all_csv = Menu(menu_dict_import_all_csv)
            menu_import_all_csv.title("추출할 CSV의 종류를 선택하세요.")
            menu_import_all_csv.run_menu()
            if menu_import_all_csv.selected_num != 3: # csv 변수추출 중 처음으로가 아님
                import_all_csv_infodict = CSVFunc().import_all_CSV(menu_import_all_csv.selected_num)
                MenuPreset().shall_save_data(import_all_csv_infodict,'infodict')
                last_work = import_all_csv_infodict # 마지막 작업 저장
        elif menu_csv.selected_num == 1:
            menu_dict_csv_srs_friendly = {0: 'csv 내 이름만',
                1: 'csv 내 변수만 (CHARA 제외)',2:'처음으로'}
            menu_csv_srs_friendly = Menu(menu_dict_csv_srs_friendly)
            menu_csv_srs_friendly.run_menu()
            if menu_csv_srs_friendly.selected_num != 2:
                csv_srs_friendly_infodict = CSVFunc().import_all_CSV(menu_csv_srs_friendly.selected_num+3)
                MenuPreset().shall_save_data(csv_srs_friendly_infodict,'infodict')
                last_work = csv_srs_friendly_infodict
        elif menu_csv.selected_num == 2:
            csvvar_dict = CSVFunc().make_csv_var_dict()
            MenuPreset().shall_save_data(csvvar_dict,'dict')
            last_work = csvvar_dict
        if menu_csv.selected_menu != '이전으로':
            last_work_name = menu_csv.selected_menu # 마지막 작업 명칭 저장
# [1] ERB 파일의 처리
    elif menu_main.selected_menu == 'ERB 파일 처리':
        print("ERB 파일 처리 유틸리티입니다. 현재 TW 파일 이외의 구동을 보장하지 않습니다.")
        menu_dict_erb = {0: '사용된 CSV 변수 추출', 1: '구상추출',
                         2: '들여쓰기 교정', 3: '이전으로'}
        menu_erb = Menu(menu_dict_erb)
        menu_erb.run_menu()
        if menu_erb.selected_num == 0:
            erb_csv_var_infodict= ERBFunc().search_csv_var()
            last_work = erb_csv_var_infodict
        elif menu_erb.selected_num == 1:
            erb_printfunc_infodict = ERBFunc().extract_printfunc()
            last_work = erb_printfunc_infodict
        elif menu_erb.selected_num == 2:
            remodeled_erb = ERBFunc().remodel_indent()
            make_erb_yn = MenuPreset().yesno("지금 바로 데이터를 erb화 할까요?")
            if make_erb_yn == 0:
                ResultFunc().make_result(menu_erb.selected_menu,remodeled_erb,1)
            MenuPreset().shall_save_data(remodeled_erb,'metatext_list')
            last_work = remodeled_erb
        if menu_erb.selected_menu != '이전으로':
            last_work_name = menu_erb.selected_menu

# [2] ERH 파일의 처리
    elif  menu_main.selected_menu == 'ERH 파일 처리 (미실장)':
        print("미실장입니다")
# [3] 결과물 제어
    elif menu_main.selected_menu == '결과물 제어':
        menu_dict_result = {0: '결과물 TXT화',1: '결과물 ERB화',
                            2: '결과물 SRS화',3: '이전으로'}
        menu_result = Menu(menu_dict_result)
        menu_result.title("추출 결과물에 대한 제어 메뉴입니다.")
        menu_result.run_menu()
        if menu_result.selected_num == 0:
            ResultFunc().make_result(last_work_name,last_work)
        elif menu_result.selected_menu == '결과물 ERB화':
            ResultFunc().make_result(last_work_name,last_work,1)
        elif menu_result.selected_menu == '결과물 SRS화':
            ResultFunc().make_result(last_work_name,last_work,2)
# [4] 프로그램 정보
    elif menu_dict_main[menu_main.selected_num] == '프로그램 정보':
        menu_dict_prginfo = {0: '버전명',1: '오류보고 관련',2: '유의사항',3: '이전으로'}
        menu_prginfo = Menu(menu_dict_prginfo)
        menu_prginfo.title('EZworkEra 정보')
        menu_prginfo.run_menu()
        if menu_prginfo.selected_num == 0:
            print("3.0.0")
        elif menu_prginfo.selected_num == 1:
            print("https://github.com/SecretU4/EZworkEra/issues 으로 연락주세요.")
        elif menu_prginfo.selected_num == 2:
            print("""
아직 완성된 프로그램이 아닙니다. 사용 시 문제가 발생하면 오류를 보고해주세요.
여러분의 도움으로 더 나은 프로그램을 만들어 노가다를 줄입니다.

현재 윈도우 환경만 지원합니다. 어차피 원본 엔진도 윈도우용이잖아요.
            """)
# [5] 프로그램 종료
    elif menu_dict_main[menu_main.selected_num] == '프로그램 종료':
        break
CommonSent.end_comment()
