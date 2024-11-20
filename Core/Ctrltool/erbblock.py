"""EraBasic 코드 블럭 판별 모듈
Class
    CheckStack
"""
from customdb import FuncInfo


class CheckStack:
    '''파일 단위 ERB 파서
    
    Functions:
        code_checker(line)
        check_lines(lines)
    Variables:
        data_label
            filename 등 데이터 대표 라벨 입력
        funcs
            처리된 함수 모음, FuncInfo형
        gotos
            처리된 goto 모음, dict형
    '''
    def __init__(self, data_label="ERBFile"):
        self.data_label = data_label
        self.funcs = FuncInfo()
        self.gotos = dict() # {cnt:label | label:lines}

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
        elif line.startswith("FOR"):
            return (4, 1, 0)
        elif line.startswith("REPEAT"):
            return (4, 1, 1)
        elif line.startswith("WHILE"):
            return (4, 1, 2)
        elif line.startswith("NEXT"):
            return (4, 3, 0)
        elif line.startswith("REND"):
            return (4, 3, 1)
        elif line.startswith("WEND"):
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
        elif line.startswith("#"): # DIM, FUNCTION 등 특수 코드
            return (0, 2, 3)
        elif line.startswith("RETURN"):  # RETURNF 도 인식함
            return (0, 3, 0)  # 함수 탈출자
        else:  # 일반문
            if line:
                return (0, 0, 2)
            return (None, None, None)  # 단순 빈줄 미처리

    def warp_func(self, s_lines, s_indexs):
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

        self.funcs.add_row(funcname, temp_lines, self.data_label, head_index)
        if backup:
            s_lines[backup[0]] = backup[1]

        if len(s_indexs): # 디버깅용
            print("완성되지 않은 블럭이 있습니다.")
            raise IndexError(s_indexs, self.data_label) # TODO 로그 파일 작성

    def warp_goto(self, g_lines:list):
        t_lines = g_lines
        label = t_lines.pop(0)
        self.gotos[label] = t_lines

    def warp_squash(self, checker:tuple, s_lines:dict, s_index:list, cnt):
        # is_squash 값 반환
        if checker == (0, 3, 2): # }
            head_index = s_index.pop()
            temp_lines = []
            for num in range(cnt - head_index):
                temp_lines.append(s_lines.pop(cnt - num))
            s_lines[head_index] = temp_lines
            return 0
        return 1
    
    def warp_sif(self, s_lines:dict, s_index:list, cnt):
        # is_sif 값 반환
        head_index = s_index.pop()
        s_lines[head_index] = [s_lines[head_index], s_lines.pop(cnt)]
        return 0

    def skip_line(self, line:str, switch):
        # 주석문 및 SKIP문 처리, 없음/종료 시 0, 시작시 1, 진행중일 때 2 반환
        if line.startswith("[SKIPSTART]"):
            return 1
        elif line.startswith("[SKIPEND]"):
            return -1
        elif switch:
            return 2
        elif line.startswith(";"):
            return -2
        return 0

    def check_lines(self, lines:list[str]):
        is_sif, is_skip, is_squash, is_goto = 0, 0, 0, 0
        stack_index = list() # len()을 code 깊이 체크용으로 사용
        stack_goto = list() #TODO 미완성
        stack_lines = dict()

        for cnt, line in enumerate(lines):
            line = line.strip()
            # 주석문 통과 선처리
            is_skip = self.skip_line(line, is_skip)
            if is_skip >= 1:
                continue
            elif is_skip <= -1:
                is_skip = 0
                continue

            checker = self.code_checker(line)
            codetype, codeinfo, codeetc = checker
            if line:
                stack_lines[cnt] = line
            else: # 공란은 통과
                continue

            if is_squash:
                is_squash = self.warp_squash(checker, stack_lines, stack_index, cnt)
            elif is_sif:
                is_sif = self.warp_sif(stack_lines, stack_index, cnt)
            elif not codetype:
                if not codeinfo:
                    if codeetc == 2: # code_checker 에서 걸러지지 못한 line
                        pass
                elif (codeinfo, codeetc) == (3, 0): # RETURN
                    if len(stack_index) == 1:
                        self.warp_func(stack_lines, stack_index)
                elif (codeinfo, codeetc) == (1, 0):  # 함수 선언문
                    if stack_index:  # RETURN으로 끝나지 않은 함수가 있을때
                        if is_goto == len(stack_index):
                            self.warp_goto(lines[stack_goto.pop():cnt])
                        self.warp_func(stack_lines, stack_index)

                    stack_index.append(cnt)
                    is_goto = 0
                elif (codeinfo, codeetc) == (1, 1):  # GOTO 시작점
                    if is_goto:
                        self.warp_goto(lines[stack_goto.pop():cnt+1])
                    is_goto = len(stack_index)
                    stack_goto.append(cnt)
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
                    self.warp_goto(lines[stack_goto.pop():cnt+1])
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
            self.warp_func(stack_lines, stack_index)

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
    a = tester.check_lines(sample.gen_bulk())
    print(tester.funcs.func_dict())
    input(a)
