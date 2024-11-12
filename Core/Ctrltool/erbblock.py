"""EraBasic 코드 블럭 판별 모듈"""


class CheckStack:
    '''파일 단위 ERB 파서'''
    def __init__(self, data_label="ERBFile"):
        self.funcs = dict()
        self.gotos = dict()
        self.func_indexs = dict()
        self.data_label = data_label

    def code_checker(self, line):
        # 함수 관련문인지 아닌지 처리
        """ 0항: 0=기타 1=IF 2=CASE 3=PRINTDATA 4=반복문\n1항: 0=단독 1=시작 2=중간 3=탈출\n2항: 비고
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
                return (3, 1, 1)
            return (3, 0, 0)
        # 반복문 처리
        elif line.startswith("REPEAT"):
            return (4, 1, 0)
        elif line.startswith("WHILE"):
            return (4, 1, 1)
        elif line.startswith("FOR"):
            return (4, 1, 2)
        elif line.startswith("REND"):
            return (4, 3, 0)
        elif line.startswith("WEND"):
            return (4, 3, 1)
        elif line.startswith("NEXT"):
            return (4, 3, 2)
        elif line.startswith("BREAK"):
            return (4, 2, 0)
        elif line.startswith("CONTINUE"):
            return (4, 2, 1)
        # 기타 처리
        elif line.startswith("@"):
            return (0, 1, 0)
        elif line.startswith("$"): # GOTO LABEL
            return (0, 1, 1)
        elif line.startswith("{"):
            return (0, 1, 2)
        elif line.startswith("}"):
            return (0, 3, 2)
        elif line.startswith("GOTO"):
            return (0, 2, 0)
        elif line.startswith("CALL"):
            return (0, 2, 1)
        elif line.startswith("BEGIN"):
            return (0, 2, 2)
        elif line.startswith("RETURN"):  # RETURNF 도 인식함
            return (0, 3, 0)  # 함수 탈출자
        else:  # 일반문
            if line:
                return (0, 0, 2)
            return (None, None, None)  # 단순 빈줄 미처리

    def organize_func(self, s_lines, s_indexs):
        '''처리된 함수 마무리'''
        head_index = s_indexs.pop()
        funcname = s_lines.get(head_index)
        temp_lines = []
        backup = None
        while len(s_lines):
            item = s_lines.popitem()
            if isinstance(item[1],str) and item[1].startswith("@"): # 함수 선언부
                if len(s_lines): # 현재 처리중이 아닌 함수가 잡힌 경우
                    backup = item
                    continue
            else:
                temp_lines.insert(0, item[1])

        self.funcs[funcname] = temp_lines
        self.func_indexs[funcname] = head_index
        if backup:
            s_lines[backup[0]] = backup[1]

        if len(s_indexs): # 디버깅용
            print("완성되지 않은 블럭이 있습니다.")
            raise IndexError(s_indexs, self.data_label) # TODO 로그 파일 작성

    def make_dict(self, lines):
        is_sif, is_skip, is_squash, is_goto = 0, 0, 0, 0
        stack_index = list() # len()을 code 깊이 체크용으로 사용
        stack_lines = dict()

        for cnt, line in enumerate(lines):
            line = line.strip()
            # 주석문 통과 선처리
            if line.startswith("[SKIPSTART]"):
                is_skip = 1
                continue
            elif line.startswith("[SKIPEND]"):
                is_skip = 0
                continue
            elif is_skip == 1 or line.startswith(";"):
                continue

            codetype, codeinfo, codeetc = self.code_checker(line)
            if line:
                stack_lines[cnt] = line
            else: # 공란은 통과
                continue

            if is_squash:
                if (codetype, codeinfo, codeetc) == (0, 3, 2): # }
                    head_index = stack_index.pop()
                    temp_lines = []
                    for num in range(cnt - head_index):
                        temp_lines.append(stack_lines.pop(cnt - num))
                    stack_lines[head_index] = temp_lines
                    is_squash = 0
            elif is_sif:
                head_index = stack_index.pop()
                stack_lines[head_index] = [stack_lines[head_index], stack_lines.pop(cnt)]
                is_sif = 0
            elif not codetype:
                if not codeinfo:
                    if codeetc == 2: # code_checker 에서 걸러지지 못한 line
                        pass
                elif (codeinfo, codeetc) == (3, 0): # RETURN
                    if len(stack_index) == 1:
                        self.organize_func(stack_lines, stack_index)
                elif (codeinfo, codeetc) == (1, 0):  # 함수 선언문
                    if stack_index:  # RETURN으로 끝나지 않은 함수가 있을때
                        self.organize_func(stack_lines, stack_index)

                    stack_index.append(cnt)
                    is_goto = 0
                elif (codeinfo, codeetc) == (1, 1):  # GOTO 시작점
                    is_goto = len(stack_index)
                    pass #TODO
                elif (codeinfo, codeetc) == (1, 2): # {
                    stack_index.append(cnt)
                    is_squash = 1
                elif (codeinfo, codeetc) == (2, 0): # GOTO 호출
                    self.gotos[cnt] = line.split(" ")[-1] # GOTO Label 이름
                    if is_goto == len(stack_index):
                        is_goto = 0

            elif codeinfo == 0:
                if codetype == 1: # SIF
                    stack_index.append(cnt)
                    is_sif = 1
            elif codeinfo == 1: # 시작
                stack_index.append(cnt)
            elif codeinfo == 2:
                pass #TODO
            elif codeinfo == 3: # 탈출
                if is_goto == len(stack_index):
                    pass
                start_index = stack_index.pop()
                temp_lines = []
                key = cnt
                while key != start_index:
                    key, val = stack_lines.popitem()
                    temp_lines.insert(0, val)
                stack_lines[start_index] = temp_lines
            else:
                raise NotImplementedError(line)

        if stack_index: # RETURN 없는 함수 정리
            self.organize_func(stack_lines, stack_index)

        return stack_lines # 디버깅용


class sample_code:
    def __init__(self, target_filename=None):
        if not target_filename:
            target_filename = input("Input File Name : ")
        self.open_gen = open(target_filename, "r", encoding="utf-8-sig")

    def gen_bulk(self):
        with self.open_gen:
            result_lines = self.open_gen.readlines()
        return result_lines


if __name__ == "__main__":
    sample = sample_code()
    tester = CheckStack("test_file")
    a = tester.make_dict(sample.gen_bulk())
    print(tester.funcs)
    input(a)
