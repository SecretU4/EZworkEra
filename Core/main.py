# EmuEra용 번역 파일 처리/합병 툴
# 사용되는 라이브러리
from util import CommonSent
from Ctrltool import CSVFunc, ERBFunc, ResultFunc
from usefile import MenuPreset
from System.interface import Menu
from System.xmlhandling import SettingXML

menu_dict_main = {
    0: "CSV 파일 처리",
    1: "ERB 파일 처리",
    2: "ERH 파일 처리 (미실장)",
    3: "결과물 제어",
    4: "프로그램 정보",
    5: "프로그램 종료",
}
menu_main = Menu(menu_dict_main)
menu_main.title("EZworkEra - Develop utility for EmuEra base game")

last_work = None
last_work_name = None

def run_main():
    global last_work
    global last_work_name
    while True:
        print("작업 후 버튼을 눌러 프로그램을 종료하셔야 작업파일이 손실되지 않습니다.")
        CommonSent.print_line()
        menu_main.run_menu()
        # [0] CSV 파일의 처리
        if menu_main.selected_menu == "CSV 파일 처리":
            CommonSent.print_line()
            menu_dict_csv = {
                0: "CSV 변수 목록 추출",
                1: "CSV 변수 명칭 사전",
                2: "이전으로",
            }
            menu_csv = Menu(menu_dict_csv)
            menu_csv.title("CSV 파일 처리 유틸리티입니다.", "따로 표기해놓지 않았다면 숫자:변수명 꼴입니다.")
            menu_csv.run_menu()
            if menu_csv.selected_num == 0:
                menu_dict_import_all_csv = {
                    0: "구별없이 모두",
                    1: "필터 설정",
                    2: "인명 SRS 작성용",
                    3: "처음으로"}
                menu_import_all_csv = Menu(menu_dict_import_all_csv)
                menu_import_all_csv.title("CSV를 추출할 내용/파일명 조건을 선택해주세요.")
                menu_no = menu_import_all_csv.run_menu()
                if menu_no == 3: # csv 변수추출 중 처음으로 이동
                    continue
                elif menu_no == 0:
                    mod_no = 0
                elif menu_no == 1:
                    mod_dict = {1:"1열/2열 반전", 2:"특수형식 csv 미포함"}
                    mod_no = MenuPreset().select_mod(
                        mod_dict, title_txt="1열/2열 반전시 특수형식 csv는 포함하지 않는 것을 권장합니다."
                        )
                elif menu_no == 2:
                    mod_no = 0b100

                import_all_csv_infodict = CSVFunc().import_all_CSV(mod_no)
                MenuPreset().shall_save_data(import_all_csv_infodict, "infodict")
                last_work = import_all_csv_infodict  # 마지막 작업 저장
            elif menu_csv.selected_num == 1:
                csvvar_dict = CSVFunc().make_csv_var_dict()
                MenuPreset().shall_save_data(csvvar_dict, "dict")
                last_work = csvvar_dict
            if menu_csv.selected_menu != "이전으로":
                last_work_name = menu_csv.selected_menu  # 마지막 작업 명칭 저장
        # [1] ERB 파일의 처리
        elif menu_main.selected_menu == "ERB 파일 처리":
            print("ERB 파일 처리 유틸리티입니다. 현재 TW 파일 이외의 구동을 보장하지 않습니다.")
            menu_dict_erb = {
                0: "ERB 내 CSV 변수 추출",
                1: "구상추출",
                2: "들여쓰기 교정",
                3: "구상 번역기",
                4: "ERB 내 CSV 인덱스 변환",
                5: "불완전 수식 정리",
                6: "이전으로",
            }
            menu_erb = Menu(menu_dict_erb)
            menu_erb.run_menu()
            if menu_erb.selected_num == 0:
                erb_csv_var_infodict = ERBFunc().search_csv_var()
                last_work = erb_csv_var_infodict
            elif menu_erb.selected_num == 1:
                erb_printfunc_infodict = ERBFunc().extract_printfunc()
                last_work = erb_printfunc_infodict
            elif menu_erb.selected_menu in ["들여쓰기 교정", "구상 번역기", "ERB 내 CSV 인덱스 변환", "불완전 수식 정리"]:
                last_work = None
                if menu_erb.selected_menu == "들여쓰기 교정":
                    remodeled_erb = ERBFunc().remodel_indent()
                    sav_datatype = "textline"
                    last_work = remodeled_erb
                elif menu_erb.selected_menu == "구상 번역기":
                    print("양식에 맞는 txt 파일을 erb 문법 파일로 바꾸어주는 유틸리티입니다.")
                    menu_list_eratype = ["TW"]
                    menu_eratype = Menu(menu_list_eratype)
                    menu_eratype.title("어느 종류의 에라인지 선택해주세요.")
                    menu_eratype.run_menu()
                    era_type = menu_eratype.selected_menu
                    if era_type in menu_list_eratype:
                        sent_load_dis = "csvvar 딕셔너리를 불러와주세요. 미선택시 추후 생성 단계로 넘어갑니다."
                        csvvar_dict = MenuPreset().load_saved_data(0, sent_load_dis)
                        complete_metainfo = ERBFunc().translate_txt_to_erb(era_type, csvvar_dict)
                        sav_datatype = "metaerb"
                        last_work = complete_metainfo
                elif menu_erb.selected_menu == "ERB 내 CSV 인덱스 변환":
                    menu_dict_erb_rep = {0: "숫자를 변수로", 1: "변수를 숫자로"}
                    menu_erb_rep = Menu(menu_dict_erb_rep)
                    mod_num = menu_erb_rep.run_menu()
                    erb_replace_csvvar_infodict = ERBFunc().replace_num_or_name(mod_num)
                    print("현재 변환된 데이터를 erb로 만들지 않았습니다. 이후 절차를 진행해주세요.")
                    sav_datatype = "erblines"
                    last_work = erb_replace_csvvar_infodict
                elif menu_erb.selected_menu == "불완전 수식 정리":
                    erb_infodict = ERBFunc().remodel_equation()
                    sav_datatype = "metainfoline"
                    last_work = erb_infodict
                if last_work != None:
                    MenuPreset().shall_save_data(last_work, sav_datatype)
                    make_erb_yn = MenuPreset().yesno(1, "지금 바로 데이터를 erb화 할까요?")
                    if make_erb_yn:
                        ResultFunc().make_result(menu_erb.selected_menu, last_work, 1)
            if menu_erb.selected_menu != "이전으로":
                last_work_name = menu_erb.selected_menu

        # [2] ERH 파일의 처리
        elif menu_main.selected_menu == "ERH 파일 처리 (미실장)":
            print("미실장입니다")

        # [3] 결과물 제어
        elif menu_main.selected_menu == "결과물 제어":
            menu_dict_result = {0: "결과물 TXT화", 1: "결과물 ERB화", 2: "결과물 SRS화", 3: "이전으로"}
            menu_result = Menu(menu_dict_result)
            menu_result.title("추출 결과물에 대한 제어 메뉴입니다.")
            menu_result.run_menu()
            if menu_result.selected_num == 0:
                ResultFunc().make_result(last_work_name, last_work)
            elif menu_result.selected_menu == "결과물 ERB화":
                ResultFunc().make_result(last_work_name, last_work, 1)
            elif menu_result.selected_menu == "결과물 SRS화":
                ResultFunc().make_result(last_work_name, last_work, 2)

        # [4] 프로그램 정보
        elif menu_dict_main[menu_main.selected_num] == "프로그램 정보":
            xml_settings = SettingXML()
            menu_dict_prginfo = {0: "버전명", 1: "오류보고 관련", 2: "유의사항", 3: "이전으로"}
            menu_prginfo = Menu(menu_dict_prginfo)
            menu_prginfo.title("EZworkEra 정보")
            menu_prginfo.run_menu()
            if menu_prginfo.selected_num == 0:
                print("버전명: " + xml_settings.show_info("version"))
            elif menu_prginfo.selected_num == 1:
                print("{}/issues 으로 연락주세요.".format(xml_settings.show_info("github")))
            elif menu_prginfo.selected_num == 2:
                print(xml_settings.show_info("caution"))

        # [5] 프로그램 종료
        elif menu_dict_main[menu_main.selected_num] == "프로그램 종료":
            break
    CommonSent.end_comment()


try:
    run_main()
except Exception as error:
    print("{}가 발생하였습니다. 로그 파일을 보내주시면 도움이 됩니다.".format(error))
    input("아무 키나 눌러 종료...")
