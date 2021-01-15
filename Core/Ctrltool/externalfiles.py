"""에라 구동계 파일 이외 처리용 모듈"""

import json
from customdb import InfoDict
from usefile import MenuPreset

class TransUserDict:
    """ezTrans용 사용자사전 처리 클래스"""
    def __init__(self,filename):
        with open(filename, "r", encoding="utf-8") as jsonfile:
            self.filedata = json.load(jsonfile)
    
    def convert_to_infodict(self):
        pd_name = "PreDic"
        ad_name = "AfterDic"
        orig_words = InfoDict("orig_words")
        trans_words = InfoDict("trans_words")

        for dict_name in (pd_name, ad_name):
            dictdata = self.filedata.get(dict_name)
            orig_dict = dict()
            trans_dict = dict()

            for order_no, key in enumerate(dictdata):
                orig_dict[order_no] = key
                trans_dict[order_no] = dictdata[key]

            orig_words.add_dict("orig\\"+dict_name, orig_dict)
            trans_words.add_dict("trans\\"+dict_name, trans_dict)
        return orig_words, trans_words


class EXTFunc:
    def userdict_to_srs(self):
        print("이지트랜스용 UserDic 파일을 srs 형태로 변환할 수 있게 합니다.")
        print("빈 칸 입력시 전으로 돌아갑니다.")
        while True:
            filename = input("변환할 UserDic 파일의 경로를 입력해주세요.(파일명, 확장자 포함)")
            if not filename:
                return False
            elif not filename.find(".json"):
                print("확장자명을 포함해 입력해주세요.")
            else:
                break
    
        transdict = TransUserDict(filename)
        result = None

        print("\n\n적어도 하나의 데이터는 .sav 파일로 저장해두셔아 srs화가 가능합니다.")

        for data in transdict.convert_to_infodict():
            print("처리된 데이터 분류: %s" % data.db_name)

            if not MenuPreset().shall_save_data(data, "infodict"):
                result = data
        if not result:
            result = data

        return result

