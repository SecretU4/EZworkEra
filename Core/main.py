"""EmuEra용 번역 파일 처리/합병 툴

각 모듈의 실행부 처리 데이터를 받아 저장하고, 이와 관련된 처리 모듈로 이관함.
실질적인 유저 인터페이스 역할.

Class:
    MainMenu
"""

__version__ = 'v4.1.1'

from util import CommonSent
from Ctrltool import CrawlFunc, CSVFunc, ERBFunc, EXTFunc, SRSFunc
from Ctrltool.result import ResultFunc
from usefile import MenuPreset
from System.interface import Menu
from System.xmlhandling import SettingXML

menu_dict_main = {
    0: '프로그램 종료',
    1: 'CSV 파일 분석',
    2: 'ERB 파일 분석',
    3: 'ERB 파일 처리',
    4: 'ERH 파일 분석 (미실장)',
    5: '외부 데이터 처리',
    6: '결과물 처리',
    7: '프로그램 정보',
}
menu_main = Menu(menu_dict_main)
menu_main.title("EZworkEra - Develop utility for EmuEra base game")

class MainMenu:
    def __init__(self):
        self.f_data = None
        self.f_name = None

    def _menu_print(self, menu_dic, *lines):
        CommonSent.print_line()
        menu = Menu(menu_dic)
        menu.title(*lines)
        m_no = menu.run_menu()
        if not m_no:
            self.f_name = None
        else:
            self.f_name = menu.selected_menu
        return m_no

    def csv_anal(self):
        menu_dict_csv = {
            0: '이전으로',
            1: 'CSV 변수 목록 추출',
            2: 'CSV 변수 명칭 사전',
        }
        m_no = self._menu_print(menu_dict_csv,
                                "CSV 파일 분석 메뉴입니다.", "따로 표기해놓지 않았다면 숫자:변수명 꼴입니다.")
        if not m_no:
            return False
        elif m_no == 1:
            menu_dict_sel_csv = {
                0: '처음으로',
                1: '필터 설정',
                2: '구별없이 모두',
                3: 'SRS 작성용 - 인명',
                4: 'SRS 작성용 - 변수명',
                }
            m_no2 = self._menu_print(menu_dict_sel_csv, "CSV를 추출할 내용/파일명 조건을 선택해주세요.")
            if not m_no2: # csv 변수추출 중 처음으로 이동
                return False
            elif m_no2 == 1:
                mod_dict = {1:'1열/2열 반전', 2:'특수형식 csv 미포함'}
                mod_no = MenuPreset().select_mod(
                    mod_dict, title_txt="1열/2열 반전시 특수형식 csv는 포함하지 않는 것을 권장합니다."
                    )
            elif m_no2 == 2:
                mod_no = 0
            elif m_no2 == 3: # 인명 SRS용 특수 항목처리
                mod_no = 0b100
            elif m_no2 == 4: # 변수 SRS용 프리셋 - 특수형식 csv 미포함만
                mod_no = 0b10

            self.f_data = CSVFunc().import_all_CSV(mod_no)
        elif m_no == 2:
            self.f_data = CSVFunc().make_csv_var_dict()

        MenuPreset().shall_save_data(self.f_data, self.f_data.__name__)

    def erb_anal(self):
        menu_dict_anal_erb = {
            0: '이전으로',
            1: 'ERB 내 CSV 변수 추출',
            2: '구상추출',
            3: 'ERB형 데이터베이스 추출',
            4: '구상 라이센스 분석'
        }
        m_no = self._menu_print(menu_dict_anal_erb, "ERB 파일 분석 메뉴입니다.")

        if not m_no:
            return False
        elif m_no == 1:
            csvvar_mod_dict = {1:'CSV당 차트 생성(비활성화시 ERB당 생성됨)'}
            csvvar_opt = MenuPreset().select_mod(csvvar_mod_dict)
            self.f_data = ERBFunc().search_csv_var(opt=csvvar_opt)
            sav_datatype = 'sheetinfo'
        elif m_no == 2:
            ext_print_mod_dict = {
                1:'차트 내 중복 자료 제거',
                2:'ERB파일당 차트 할당(비활성화시 차트 하나에 전부 포함)',
                3:'공백을 포함하지 않음',
                4:'주석추출 모드'
                }
            ext_print_opt = MenuPreset().select_mod(ext_print_mod_dict)
            self.f_data = ERBFunc().extract_printfunc(opt=ext_print_opt)
            sav_datatype = 'sheetinfo'
        elif m_no == 3:
            self.f_data = ERBFunc().db_erb_finder()
            sav_datatype = 'erblines'
        elif m_no == 4:
            self.f_data = ERBFunc().licence_checker()
            if isinstance(self.f_data, list):
                sav_datatype = 'txtlines' 
            else:
                sav_datatype = 'InfoDict'

        if self.f_data != None:
            MenuPreset().shall_save_data(self.f_data, sav_datatype)

    def erb_proc(self):
        menu_dict_erb = {
            0: '이전으로',
            1: '들여쓰기 교정',
            2: '구상 번역기',
            3: 'ERB 내 CSV 인덱스 변환',
            4: '불완전 수식 정리',
            5: '구상 메모리 최적화',
        }
        m_no = self._menu_print(menu_dict_erb,
                                "ERB 파일 처리 메뉴입니다.", "현재 TW 파일 이외의 정상 구동을 보장하지 않습니다.")
        if not m_no:
            return False
        elif self.f_name == '들여쓰기 교정':
            self.f_data = ERBFunc().remodel_indent()
            sav_datatype = 'erblines'
        elif self.f_name == '구상 번역기': # v3.7.0 현재 알파버전
            print("양식에 맞는 txt 파일을 erb 문법 파일로 바꾸어주는 유틸리티입니다.")
            menu_list_eratype = ['TW']
            menu_eratype = Menu(menu_list_eratype)
            menu_eratype.title("어느 종류의 에라인지 선택해주세요.")
            menu_eratype.run_menu()
            if menu_eratype.selected_menu in menu_list_eratype:
                sent_load_dis = "csvvar 딕셔너리를 불러와주세요. 미선택시 추후 생성 단계로 넘어갑니다."
                csvvar_dict = MenuPreset().load_saved_data(0, sent_load_dis)
                self.f_data = ERBFunc().translate_txt_to_erb(menu_eratype.selected_menu, csvvar_dict)
                sav_datatype = 'metaerb'
        elif self.f_name == 'ERB 내 CSV 인덱스 변환':
            menu_dict_erb_rep = {0: '숫자를 변수로', 1: '변수를 숫자로'}
            menu_erb_rep = Menu(menu_dict_erb_rep)
            mod_num = menu_erb_rep.run_menu()
            self.f_data = ERBFunc().replace_num_or_name(mod_num)
            sav_datatype = 'erblines'
        elif self.f_name == '불완전 수식 정리':
            self.f_data = ERBFunc().remodel_equation()
            sav_datatype = 'metainfoline'
        elif self.f_name == '구상 메모리 최적화': # 3.7.0 현재 베타버전
            self.f_data = ERBFunc().memory_optimizer()
            sav_datatype = 'erblines'

        if self.f_data != None:
            MenuPreset().shall_save_data(self.f_data, sav_datatype)
            print("결과물을 ERB로 출력하시고 싶은 경우 추가 절차를 진행해주세요.")
            if MenuPreset().yesno("지금 바로 데이터를 erb화 할까요?"):
                self.res_proc(1)

    def erh_anal(self):
        pass

    def etc_proc(self):
        menu_dict_other_data = {
            0: '이전으로',
            1: 'UserDic.json srs화',
            2: '웹 게시글 txt화',
            3: 'srs 병합',
        }
        m_no = self._menu_print(menu_dict_other_data, "era 파일과 관련성이 적은 데이터의 처리 메뉴입니다.")
        if not m_no:
            return False
        elif 'srs' in self.f_name:
            if self.f_name == 'UserDic.json srs화':
                self.f_data = EXTFunc().userdict_to_srs()
            elif self.f_name == 'srs 병합':
                self.f_data = SRSFunc().merge_srs()

            if self.f_data:
                if MenuPreset().yesno("바로 srs화를 진행할까요?"):
                    self.res_proc(2)
                else:
                    input("저장된 infodict 데이터를 기반으로 '결과물 srs화'를 해주셔야 srs화가 되니 참고해주세요.")
        elif self.f_name == '웹 게시글 txt화':
            self.f_data = CrawlFunc().crawl_text()
            if self.f_data:
                print("바로 txt화를 진행합니다.")
                self.res_proc(1)

        if not self.f_data:
            input("작업한 내용이 없습니다.")
            return False

    def res_proc(self, opt=0):
        if not opt:
            menu_dict_result = {
                0: '이전으로',
                1: '결과물 TXT화',
                2: '결과물 ERB화',
                3: '결과물 srs화',
                4: '결과물 xlsx화',
                }
            m_no = self._menu_print(menu_dict_result, "추출 결과물에 대한 제어 메뉴입니다.")
            if not m_no:
                return False
            opt = m_no - 1

        ResultFunc().make_result(self.f_name, self.f_data, opt)

    def info(self):
        xml_settings = SettingXML()
        menu_dict_prginfo = {0: '이전으로', 1: '버전명', 2: '오류보고 관련', 3: '유의사항'}
        m_no = self._menu_print(menu_dict_prginfo, "EZworkEra 정보")

        if m_no == 1:
            print("버전명: " + __version__)
        elif m_no == 2:
            print("{}/issues 으로 연락주세요.".format(xml_settings.show_info('github')))
        elif m_no == 3:
            print(xml_settings.show_info('caution'))


def run_main():
    home = MainMenu()
    menu_connect = {
        menu_dict_main[1]: home.csv_anal,menu_dict_main[2]: home.erb_anal,
        menu_dict_main[3]: home.erb_proc,
        menu_dict_main[5]: home.etc_proc,menu_dict_main[6]: home.res_proc,
        menu_dict_main[7]: home.info
    }

    while True:
        print("작업 후 버튼을 눌러 프로그램을 종료하셔야 작업파일이 손실되지 않습니다.")
        CommonSent.print_line()
        menu_main.run_menu()

        if menu_main.selected_menu == '프로그램 종료':
            break
        elif menu_main.selected_menu == 'ERH 파일 분석 (미실장)':
            # last_work, last_menu = home.erh_anal()
            print("미실장입니다")
        else:
            menu_connect.get(menu_main.selected_menu)()
    CommonSent.end_comment()

try:
    run_main()
except Exception as error:
    print("{}가 발생하였습니다. 로그 파일을 보내주시면 도움이 됩니다.".format(error))
    input("아무 키나 눌러 종료...")
