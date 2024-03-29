# #DIM 등 전역변수/지역변수 처리 관련 모듈
from customdb import InfoDict
from usefile import CustomInput, LoadFile, LogPreset, MenuPreset
from util import CommonSent, DataFilter


class ERHLoad(LoadFile):
    def __init__(self, NameDir, EncodeType):
        super().__init__(NameDir, EncodeType)


class HandleDIM:
    def __init__(self, dim_dict: dict[str, list] = dict()):
        self.dim_dict = dim_dict

    def __del_dim_mid(self, words:list[str]) -> list[str]:  # TODO 호출자 따른 변동 가능하도록
        """DIM 관련 중간 식별자 제거 함수"""
        dim_mid = ("#DIM", "#DIMS", "DYNAMIC", "CONST", "SAVEDATA", "CHARADATA", "GLOBAL", "REF")
        temp = words.copy()

        if not words[0] in dim_mid:
            return words
        else:
            temp.pop(0)
            return self.__del_dim_mid(temp)

    def dim_search(self, line: str):  # TODO DIM 작동방식 추가분석 필요
        is_defined = False
        array_list: list[str] = []  # 차원수
        defined_list: list[str] = []  # 초기값수
        result: list[str] = []
        temp_dimdict: dict[str, result] = dict()

        words = line.split()
        if not line.startswith("#DIM"):
            return temp_dimdict
        words = self.__del_dim_mid(words)
        dim_name = words.pop(0).split(",")[0]
        dim_name.strip()

        for word in words:
            word = word.replace(",", "").strip()
            if word in ("="):
                is_defined = True
            elif is_defined:
                defined_list.append(word)
            elif word.isdecimal():
                array_list.append(word)

        if array_list:  # 다차원 지원
            len_array = len(array_list)
            if len_array == 1:  # 1차원
                for count in range(array_list[0]):
                    result.append("0")
            else:
                print("2차원 이상의 배열은 현재 지원하지 않습니다. 현재: %d차원" % len_array)
        elif defined_list:  # 초기값 있을때
            for count, arg in enumerate(defined_list):
                result.insert(count, arg)
        else:  # 초기값 미설정
            result.append("0")

        temp_dimdict[dim_name] = result
        self.dim_dict.update(temp_dimdict)
        return temp_dimdict


class ERHFunc:
    def analyze_erh(self, erh_files=None, encode_type=None):  # TODO 본격적으로 만져야함
        """return (ERH_infodict, 구동중 통합 dim_dict)"""
        if not erh_files or not encode_type:
            erh_files, encode_type = CustomInput("ERH").get_filelist()
        clsdim = HandleDIM()
        infodict = InfoDict("ERHInfoDict")

        for erhname in erh_files:
            temp_dimdict = dict()
            lines = ERHLoad(erhname, encode_type).make_bulklines()
            for line in lines:
                line.strip()
                if line.startswith(";"):
                    continue
                words = line.split()
                if not words:
                    continue
                elif words[0].startswith("#DIM"):
                    temp_dimdict.update(clsdim.dim_search(line))
            infodict.add_dict(erhname, temp_dimdict)

        return infodict, clsdim.dim_dict

    def make_dimdict(self):
        pass
