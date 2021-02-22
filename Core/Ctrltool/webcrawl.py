"""웹 크롤링 관련 모듈"""

import requests
from bs4 import BeautifulSoup

class WebCrawl:
    def open_html(self, url):
        return requests.get(url)

    def html_obj(self, url):
        return BeautifulSoup(self.open_html(url).content, "html.parser")


class ArcaliveCrawl(WebCrawl):
    # SSL 인증서 관련 문제 발생시 crypto/ssl dll 문제임.
    def __init__(self, url):
        self.url = url
        self.object = self.html_obj(url)

    def txt_data(self):
        lines = []
        main_context = self.html_obj(self.url).body.find("div", {"class":"fr-view article-content"})
        p_lines = main_context.find_all("p")
        for p_line in p_lines:
            lines.append(p_line.text + "\n")
        return lines


class CrawlFunc:
    def crawl_text(self):
        """웹페이지 내 텍스트를 크롤링하는 함수"""
        print("현재 ArcaLive 내 게시글만 지원합니다.")
        while True:
            print("입력하신 웹페이지 내 텍스트 내용을 크롤링합니다. 공란인 경우 이전으로 돌아갑니다.")
            target_url = input("크롤링할 웹페이지 url를 입력해주세요. http나 https가 포함되어야 합니다. : ")
            if not target_url: # 공란 입력
                return None
            elif target_url.find("arca.live"): 
                html_data = ArcaliveCrawl(target_url)
                result_data = html_data.txt_data()
                break
            else: # 도메인이 아카라이브가 아님
                print("현재 ArcaLive 내 게시글만 지원합니다.")

        if not result_data:
            print("크롤링된 데이터가 없습니다.")
        
        print("결과물 제어 - txt화를 통해 크롤링된 데이터를 출력하실 수 있습니다.")

        return result_data

if __name__ == "__main__":
    print("베타 테스트입니다.")
    lines = CrawlFunc().crawl_text()
    f_name = input("저장시킬 파일명을 입력해주세요.")
    f_open = open(f_name + ".txt", "w", encoding="UTF-8").writelines(lines)
