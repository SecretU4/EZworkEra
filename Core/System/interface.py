"""프로그램 내에서 사용자에게 보여주는 인터페이스 관련 모듈.

Classes:
    Menu
    StatusNum
"""

import time
import os
import re
from util import CommonSent, KoreanSupport


class Menu:
    """입력받은 자료형({int:str} 또는 [str]) 기반 메뉴창 표출 및 입력값 받음.
    * dict의 경우 '돌아가기'가 생성되지 않음.

    Functions:
        title(str)
        run_menu()

    Variables:
        selected_num
        selected_menu
    """

    def __init__(self, menu_data):
        self.window_size = os.get_terminal_size().columns
        if isinstance(menu_data, dict):
            for key in list(menu_data.keys()):
                if re.compile("[^0-9]").match(str(key)):
                    raise TypeError
            self.menu_dict = menu_data
        elif isinstance(menu_data, list):
            menu_data.insert(0, "돌아가기")
            self.menu_dict = {}
            for keyname in menu_data:  # 리스트 목록 번호 부여
                self.menu_dict[menu_data.index(keyname)] = keyname
        else:
            raise TypeError

    def __print_menu(self):
        for key in self.menu_dict:
            print("[{}]. {}".format(key, self.menu_dict[key]))
        CommonSent.print_line()
        return input("번호를 입력하세요. 클릭은 지원하지 않습니다. :")

    # TODO 항목 50개 초과시 페이지 정렬 지원
    def __print_paged_menu(self):
        """우선순위 페이지를 제공하는 메뉴 출력 옵션. 원 menu_data가 list인 경우만 상정함."""
        copy_menudict = self.menu_dict.copy()
        prior_menulist = list()
        others_menulist = list()
        comp_values = dict()
        is_prior_now = True

        for key, value in self.menu_dict.items():
            if "All" in value or "ONLY" in value:
                value = copy_menudict.pop(key)
                prior_menulist.append(value)
            else:
                value = copy_menudict[key]
                others_menulist.append(value)
            comp_values[value] = key

        while True: # 2페이지인 경우만 상정함.(우선페이지/나머지)
            # 2페이지를 만들 수 없는 경우
            if not prior_menulist or len(others_menulist) <= 1: # (others의 경우 돌아가기만 있는 경우 있음)
                to_work = ()
                target_menulist = self.menu_dict
            else:
                if is_prior_now: # 우선 페이지 상황
                    to_work = ("다음 페이지", "이전 페이지")
                    target_menulist = prior_menulist.copy()
                else:
                    to_work = ("이전 페이지", "다음 페이지")
                    target_menulist = others_menulist.copy()
    
                target_menulist.append(to_work[0])
                try:
                    target_menulist.remove(to_work[1])
                except ValueError:
                    pass

            menu_paged = Menu(target_menulist)
            menu_paged.run_menu()
            if menu_paged.selected_menu in to_work:
                is_prior_now = not is_prior_now
                continue
            else:
                selected_num = comp_values.get(menu_paged.selected_menu)
                if selected_num != None:
                    break
        return selected_num

    def title(self, *title_names):
        """메뉴 제목용 함수. 메뉴 내 문장 출력에도 사용 가능"""
        CommonSent.print_line()
        for title_name in title_names:
            print(title_name.center(self.window_size, " "))
        CommonSent.print_line()

    def run_menu(self):
        """입력 정보를 int로 변환 후 해당하는 선택지가 있을 때 해당 숫자 반환함. 다른 경우 루프."""
        menu_numlist = tuple(self.menu_dict.keys())
        while True:
            selected_num = self.__print_menu()
            try:
                selected_num = int(selected_num)
                if menu_numlist.count(selected_num) == True:
                    self.selected_menu = self.menu_dict[selected_num]
                    return selected_num
                # EasterEgg
                elif selected_num in (4, 99, 127, 255, 999, 32767, 65535, 2147483647):
                    print("디버그 기능 없습니다!")
                    time.sleep(0.5)
                elif selected_num == 10:
                    input("지켜보고 있다" * 500)
                else:
                    CommonSent.not_ok()
            except ValueError:
                CommonSent.not_ok()

    def run_paged_menu(self):
        while True:
            selected_num = self.__print_paged_menu()
            try:
                selected_num = int(selected_num)
                if self.menu_dict.get(selected_num):
                    self.selected_menu = self.menu_dict[selected_num]
                    return selected_num
                else:
                    CommonSent.not_ok()
            except ValueError:
                CommonSent.not_ok()


class StatusNum:
    """숫자 상태 처리 관련 클래스.

    Required args:
        target_data - 작업 대상물(반복 가능한것)

    Optional args:
        target_type
            작업 대상물 타입
        logname
            해당 작업에서의 로그파일명

    Functions:
        how_much_there()
        how_much_done()

    Variables:
        counted_num
            지금까지 작업한 수
        error_num
            작업 도중 발생한 에러의 수. 작업 중 외부 입력절차 필요.
    """

    def __init__(self, target_data, target_type="jobs", logname=None, counted_num=0, error_num=0):
        """인자 설명(모듈에 쓴 것 제외):

            when_num_show
                how_much_done()에서 몇번째 파일이 완료되었을 때 문장을 출력할지를 지정.
        """
        self.total_num = len(target_data)
        self.counted_num = counted_num
        self.target_type = target_type
        self.error_num = error_num
        self.logname = logname
        if self.total_num < 10:
            self.when_num_show = [int(self.total_num / 2)]
        elif 10 <= self.total_num < 500:
            self.when_num_show = list(
                map(lambda x: x * int(round(self.total_num) / 4), list(range(1, 5)))
            )
        else:
            self.when_num_show = list(
                map(lambda x: x * int(round(self.total_num) / 10), list(range(1, 11)))
            )
        self.when_num_show.insert(0, 1)

    def how_much_there(self):
        """작업 시작시 작업물 개수 출력 함수."""
        print(
            "{} 개의 {}{} 발견되었습니다.".format(
                self.total_num, self.target_type, KoreanSupport().what_next(self.target_type, "가")
            )
        )

    def how_much_done(self):
        """진행도 확인 함수. 반복문 블럭 안 맨 뒤에 넣는다.
        * logname 작성시 오류 발생한 경우 해당 문자열 출력함.
        """
        self.counted_num += 1
        if self.counted_num in self.when_num_show:
            print("{}/{} 완료".format(self.counted_num, self.total_num))
        elif self.counted_num == self.total_num:
            if self.error_num != 0:
                print("{} 개가 정상적으로 처리되지 않았습니다.".format(self.error_num))
                if self.logname != None:
                    print("{}를 확인해주세요.".format(self.logname))
            print(
                "총 {} 개의 {} 중 {} 개가 처리 완료되었습니다.".format(
                    self.total_num, self.target_type, self.total_num - self.error_num
                )
            )


# TODO GUI 인터페이스 지원 - 구상 번역기만이라도.
