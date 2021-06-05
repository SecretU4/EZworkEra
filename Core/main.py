# EmuEra용 번역 파일 처리/합병 툴
# 사용되는 라이브러리
from util import CommonSent
from Ctrltool import CrawlFunc, CSVFunc, ERBFunc, EXTFunc, SRSFunc
from Ctrltool.result import ResultFunc
from usefile import MenuPreset
from System.interface import Menu
from System.xmlhandling import SettingXML

menu_dict_main = {
    0: "프로그램 종료",
    1: "CSV 파일 분석",
    2: "ERB 파일 분석",
    3: "ERB 파일 처리",
    4: "ERH 파일 분석 (미실장)",
    5: "외부 데이터 처리",
    6: "결과물 처리",
    7: "프로그램 정보",
}
menu_main = Menu(menu_dict_main)
menu_main.title("EZworkEra - Develop utility for EmuEra base game")

last_work = None
last_work_name = None
version_no = "v4.0.0"

def run_main():
    global last_work
    global last_work_name
    global version_no
    while True:
        print("작업 후 버튼을 눌러 프로그램을 종료하셔야 작업파일이 손실되지 않습니다.")
        CommonSent.print_line()
        menu_main.run_menu()

        # [0] 프로그램 종료
        if menu_main.selected_menu == "프로그램 종료":
            break

        # [1] CSV 파일의 분석
        elif menu_main.selected_menu == "CSV 파일 분석":
            CommonSent.print_line()
            menu_dict_csv = {
                0: "이전으로",
                1: "CSV 변수 목록 추출",
                2: "CSV 변수 명칭 사전",
            }
            menu_csv = Menu(menu_dict_csv)
            menu_csv.title("CSV 파일 분석 메뉴입니다.", "따로 표기해놓지 않았다면 숫자:변수명 꼴입니다.")
            no_csvmenu = menu_csv.run_menu()
            if not no_csvmenu: # 이전으로
                continue
            elif no_csvmenu == 1:
                menu_dict_import_all_csv = {
                    0: "처음으로",
                    1: "필터 설정",
                    2: "구별없이 모두",
                    3: "SRS 작성용 - 인명",
                    4: "SRS 작성용 - 변수명",
                    }
                menu_import_all_csv = Menu(menu_dict_import_all_csv)
                menu_import_all_csv.title("CSV를 추출할 내용/파일명 조건을 선택해주세요.")
                no_impcsv_menu = menu_import_all_csv.run_menu()
                if not no_impcsv_menu: # csv 변수추출 중 처음으로 이동
                    continue
                elif no_impcsv_menu == 1:
                    mod_dict = {1:"1열/2열 반전", 2:"특수형식 csv 미포함"}
                    mod_no = MenuPreset().select_mod(
                        mod_dict, title_txt="1열/2열 반전시 특수형식 csv는 포함하지 않는 것을 권장합니다."
                        )
                elif no_impcsv_menu == 2:
                    mod_no = 0
                elif no_impcsv_menu == 3: # 인명 SRS용 특수 항목처리
                    mod_no = 0b100
                elif no_impcsv_menu == 4: # 변수 SRS용 프리셋 - 특수형식 csv 미포함만
                    mod_no = 0b10

                import_all_csv_infodict = CSVFunc().import_all_CSV(mod_no)
                MenuPreset().shall_save_data(import_all_csv_infodict, "infodict")
                last_work = import_all_csv_infodict  # 마지막 작업 저장
            elif no_csvmenu == 2:
                csvvar_dict = CSVFunc().make_csv_var_dict()
                MenuPreset().shall_save_data(csvvar_dict, "dict")
                last_work = csvvar_dict

            last_work_name = menu_csv.selected_menu  # 마지막 작업 명칭 저장

        # [2] ERB 파일의 분석
        elif menu_main.selected_menu == "ERB 파일 분석":
            menu_dict_anal_erb = {
                0: "이전으로",
                1: "ERB 내 CSV 변수 추출",
                2: "구상추출",
                3: "ERB형 데이터베이스 추출"
            }
            menu_anal_erb = Menu(menu_dict_anal_erb)
            menu_anal_erb.title("ERB 파일 분석 메뉴입니다.")
            no_erbmenu = menu_anal_erb.run_menu()
            if not no_erbmenu: # 이전으로
                continue
            elif no_erbmenu == 1:
                csvvar_mod_dict = {1:"CSV당 차트 생성(비활성화시 ERB당 생성됨)"}
                csvvar_opt = MenuPreset().select_mod(csvvar_mod_dict)
                last_work = ERBFunc().search_csv_var(opt=csvvar_opt)
                sav_datatype = "sheetinfo"
            elif no_erbmenu == 2:
                ext_print_mod_dict = {
                    1:"차트 내 중복 자료 제거",
                    2:"ERB파일당 차트 할당(비활성화시 차트 하나에 전부 포함)",
                    3:"공백을 포함하지 않음",
                    4:"주석추출 모드"
                    }
                ext_print_opt = MenuPreset().select_mod(ext_print_mod_dict)
                last_work = ERBFunc().extract_printfunc(opt=ext_print_opt)
                sav_datatype = "sheetinfo"
            elif no_erbmenu == 3:
                last_work = ERBFunc().db_erb_finder()
                sav_datatype = "erblines"

            if last_work != None:
                MenuPreset().shall_save_data(last_work, sav_datatype)

            last_work_name = menu_anal_erb.selected_menu # 마지막 작업 명칭 저장

        # [3] ERB 파일의 처리
        elif menu_main.selected_menu == "ERB 파일 처리":
            menu_dict_erb = {
                0: "이전으로",
                1: "들여쓰기 교정",
                2: "구상 번역기",
                3: "ERB 내 CSV 인덱스 변환",
                4: "불완전 수식 정리",
                5: "구상 메모리 최적화",
            }
            menu_erb = Menu(menu_dict_erb)
            menu_erb.title("ERB 파일 처리 메뉴입니다.", "현재 TW 파일 이외의 정상 구동을 보장하지 않습니다.")
            no_erbmenu = menu_erb.run_menu()
            if not no_erbmenu: # 이전으로
                continue

            last_work = None

            if menu_erb.selected_menu == "들여쓰기 교정":
                last_work = ERBFunc().remodel_indent()
                sav_datatype = "erblines"
            elif menu_erb.selected_menu == "구상 번역기": # v3.7.0 현재 알파버전
                print("양식에 맞는 txt 파일을 erb 문법 파일로 바꾸어주는 유틸리티입니다.")
                menu_list_eratype = ["TW"]
                menu_eratype = Menu(menu_list_eratype)
                menu_eratype.title("어느 종류의 에라인지 선택해주세요.")
                menu_eratype.run_menu()
                if menu_eratype.selected_menu in menu_list_eratype:
                    sent_load_dis = "csvvar 딕셔너리를 불러와주세요. 미선택시 추후 생성 단계로 넘어갑니다."
                    csvvar_dict = MenuPreset().load_saved_data(0, sent_load_dis)
                    last_work = ERBFunc().translate_txt_to_erb(menu_eratype.selected_menu, csvvar_dict)
                    sav_datatype = "metaerb"
            elif menu_erb.selected_menu == "ERB 내 CSV 인덱스 변환":
                menu_dict_erb_rep = {0: "숫자를 변수로", 1: "변수를 숫자로"}
                menu_erb_rep = Menu(menu_dict_erb_rep)
                mod_num = menu_erb_rep.run_menu()
                last_work = ERBFunc().replace_num_or_name(mod_num)
                sav_datatype = "erblines"
            elif menu_erb.selected_menu == "불완전 수식 정리":
                last_work = ERBFunc().remodel_equation()
                sav_datatype = "metainfoline"
            elif menu_erb.selected_menu == "구상 메모리 최적화": # 3.7.0 현재 베타버전
                last_work = ERBFunc().memory_optimizer()
                sav_datatype = "erblines"

            if last_work != None:
                MenuPreset().shall_save_data(last_work, sav_datatype)
                print("결과물을 ERB로 출력하시고 싶은 경우 추가 절차를 진행해주세요.")
                if MenuPreset().yesno("지금 바로 데이터를 erb화 할까요?"):
                    ResultFunc().make_result(menu_erb.selected_menu, last_work, 1)

            last_work_name = menu_erb.selected_menu # 마지막 작업 명칭 저장

        # [4] ERH 파일의 분석
        elif menu_main.selected_menu == "ERH 파일 분석 (미실장)":
            print("미실장입니다")

        # [5] 외부 데이터 처리
        elif menu_main.selected_menu == "외부 데이터 처리":
            menu_dict_other_data = {
                0: "이전으로",
                1: "UserDic.json srs화",
                2: "웹 게시글 txt화",
                3: "srs 병합",
            }
            menu_other_data = Menu(menu_dict_other_data)
            menu_other_data.title("에라 파일과 관련성이 적은 데이터의 처리 메뉴입니다.")
            no_othermenu = menu_other_data.run_menu()
            
            if not no_othermenu: # 이전으로
                continue

            last_work_name = menu_other_data.selected_menu

            if "srs" in last_work_name:
                if last_work_name == "UserDic.json srs화":
                    last_work = EXTFunc().userdict_to_srs()
                elif last_work_name == "srs 병합":
                    last_work = SRSFunc().merge_srs()

                if not last_work:
                    input("작업한 내용이 없습니다.")
                    continue
                elif MenuPreset().yesno("바로 srs화를 진행할까요?"):
                    ResultFunc().make_result(last_work_name, last_work, 2)
                else:
                    input("저장된 infodict 데이터를 기반으로 '결과물 srs화'를 해주셔야 srs화가 되니 참고해주세요.")

            elif last_work_name == "웹 게시글 txt화":
                last_work = CrawlFunc().crawl_text()
                if last_work == None:
                    input("작업한 내용이 없습니다.")
                    continue

                print("바로 txt화를 진행합니다.")
                ResultFunc().make_result(last_work_name, last_work)

        # [6] 결과물 처리
        elif menu_main.selected_menu == "결과물 처리":
            menu_dict_result = {
                0: "이전으로",
                1: "결과물 TXT화",
                2: "결과물 ERB화",
                3: "결과물 srs화",
                4: "결과물 xlsx화",
                }
            menu_result = Menu(menu_dict_result)
            menu_result.title("추출 결과물에 대한 제어 메뉴입니다.")
            no_resultmenu = menu_result.run_menu()
            if not no_resultmenu:
                continue

            ResultFunc().make_result(last_work_name, last_work, no_resultmenu - 1)
            # 결과물 처리 이후 last_work, last_work_name 은 초기화되지 않음

        # [7] 프로그램 정보
        elif menu_main.selected_menu == "프로그램 정보":
            xml_settings = SettingXML()
            menu_dict_prginfo = {0: "이전으로", 1: "버전명", 2: "오류보고 관련", 3: "유의사항"}
            menu_prginfo = Menu(menu_dict_prginfo)
            menu_prginfo.title("EZworkEra 정보")
            no_proginfo = menu_prginfo.run_menu()
            if no_proginfo == 1:
                print("버전명: " + version_no)
            elif no_proginfo == 2:
                print("{}/issues 으로 연락주세요.".format(xml_settings.show_info("github")))
            elif no_proginfo == 3:
                print(xml_settings.show_info("caution"))

    CommonSent.end_comment()

try:
    run_main()
except Exception as error:
    print("{}가 발생하였습니다. 로그 파일을 보내주시면 도움이 됩니다.".format(error))
    input("아무 키나 눌러 종료...")
