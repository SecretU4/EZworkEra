"""EraBasic 코드 블럭 판별 모듈"""


class CheckStack:
    def __init__(self, bunch_code):
        self.bunch_code = bunch_code  # readlines 이용 리스트

    def code_checker(self, line):
        # 함수 관련문인지 아닌지 처리
        """ 0항: 0=기타 1=IF 2=CASE 3=PRINTDATA\n1항: 0=단독 1=시작 2=중간 3=탈출\n2항: 비고
        """
        if line.startswith("PRINT"):
            if line.startswith("PRINTDATA"):
                return (3, 1, 0)
            elif line.startswith("PRINTBUTTON"):
                return (0, 0, 1)
            return (0, 0, 0)
        elif line.startswith(";"):
            return (None, None, None)  # 주석은 미처리
        # 조건문 처리
        elif line.startswith("IF"):
            return (1, 1, 0)
        elif line.startswith("ELSE"):
            if line.startswith("ELSEIF"):  # 다항조건문의 1 ~ -2 번째 항
                return (1, 2, 0)
            else:  # 다항조건문의 -1항
                return (1, 2, 1)
        elif line.startswith("SIF"):  # 한줄짜리 IF문. 탈출자 없음
            return (1, 0, 0)
        elif line.startswith("ENDIF"):  # 탈출자
            return (1, 3, 0)
        # 분기문 처리
        elif line.startswith("CASE"):
            if line.startswith("CASEELSE"):
                return (2, 2, 1)
            return (2, 2, 0)
        elif line.startswith("SELECTCASE"):
            return (2, 1, 0)
        elif line.startswith("END"):
            if line.startswith("ENDLIST"):
                return (3, 3, 1)
            elif line.startswith("ENDDATA"):
                return (3, 3, 0)
            elif line.startswith("ENDSELECT"):
                return (2, 3, 0)
        elif line.startswith("DATA"):
            if line.startswith("DATAFORM"):
                return (3, 0, 0)
            elif line.startswith("DATALIST"):
                return (3, 2, 0)
        # 기타 처리
        elif line.startswith("@"):
            return (0, 1, 0)
        elif line.startswith("$"):
            return (0, 2, 0)
        elif line.startswith("RETURN"):  # RETURNF 도 인식함
            return (0, 3, 0)  # 함수 탈출자
        else:  # 일반문
            if line:
                return (0, 0, 1)
            return (None, None, None)  # 단순 빈줄 미처리

    def line_divider(self):
        bef_line_cnt = 0
        sif_switch = 0
        skip_switch = 0  # ;주석문, SKIP문 대응
        start_stack = list()  # 코드 시작지점 index
        start_end_que = list()  # 코드 시작/끝 index
        crit_stack = list()  # 함수 시작지점 index
        self.bulkdict = dict()  # {index:line} 또는 {index:block}

        for index_line in enumerate(self.bunch_code):
            line_cnt, line = index_line
            line = line.strip()
            if line.startswith("[SKIPSTART]"):
                skip_switch = 1
            elif line.startswith("[SKIPEND]"):
                skip_switch = 0
            elif skip_switch == 1 or line.startswith(";"):
                continue
            codetype, codeinfo, codeetc = self.code_checker(line)
            if line:
                self.bulkdict[line_cnt] = line
            if sif_switch:
                if codetype == None:
                    pass
                start_index = start_stack.pop()
                start_end_que.append((start_index, line_cnt))
                sif_switch = 0
            elif not codetype:
                if not codeinfo:
                    pass
                elif (codeinfo, codeetc) == (1, 0):  # 함수 선언문
                    if crit_stack:  # RETURN으로 끝나지 않은 함수가 있을때
                        com_index = crit_stack.pop()
                        start_end_que.append((com_index, bef_line_cnt + 1))
                        self.bulkdict[bef_line_cnt + 1] = ""  # 원본 손상 가능성 존재
                    crit_stack.append(line_cnt)
                elif (codeinfo, codeetc) == (2, 0):  # GOTO 시작점
                    pass
                elif codeinfo == 3:  # RETURN
                    if start_stack:
                        pass
                    else:
                        com_index = crit_stack.pop()
                        start_end_que.append((com_index, line_cnt))
            elif codetype == 1:  # IF문
                if codeinfo == 1:
                    start_stack.append(line_cnt)
                elif codeinfo == 3:
                    start_index = start_stack.pop()
                    start_end_que.append((start_index, line_cnt))
                elif codeinfo == 0:
                    start_stack.append(line_cnt)
                    sif_switch = 1
            elif codetype == 2:  # CASE문
                if codeinfo == 1:
                    start_stack.append(line_cnt)
                elif codeinfo == 3:
                    start_index = start_stack.pop()
                    start_end_que.append((start_index, line_cnt))
            elif codetype == 3:  # DATA문
                if (codeinfo, codeetc) == (1, 0):
                    start_stack.append(line_cnt)
                elif (codeinfo, codeetc) == (3, 0):
                    start_index = start_stack.pop()
                    start_end_que.append((start_index, line_cnt))
            else:
                raise NotImplementedError(line)
            bef_line_cnt = line_cnt

        for checker in start_end_que:
            if not isinstance(checker, tuple):
                raise TypeError(checker)
            block_temp = list()
            keys = list(self.bulkdict.keys())
            keys.sort()
            start_index = keys.index(checker[0])
            end_index = keys.index(checker[1])
            index_targets = keys[start_index : end_index + 1]
            for key in index_targets:
                line = self.bulkdict.pop(key)
                block_temp.append(line)
            self.bulkdict[index_targets[0]] = tuple(block_temp)

        if start_stack or crit_stack:
            print("완성되지 않은 블럭이 있습니다.")  # TODO 로그 파일 작성
        return self.bulkdict


class sample_code:
    def __init__(self, target_filename=None):
        if not target_filename:
            target_filename = input("Input File Name : ")
        self.open_gen = open(target_filename, "r", encoding="UTF-8")

    def gen_bulk(self):
        with self.open_gen:
            result_lines = self.open_gen.readlines()
        return result_lines


if __name__ == "__main__":
    sample = sample_code()
    tester = CheckStack(sample.gen_bulk())
    print(tester.line_divider())
