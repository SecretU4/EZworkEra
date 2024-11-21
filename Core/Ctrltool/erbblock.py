"""EraBasic 코드 블럭 판별 모듈
Class
    CheckStack
    MetaERB
"""
from customdb import ERBInfo, FuncInfo


class CheckStack:
    """ERB 단위 EraBasic block 파서
    
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
    """
    def __init__(self, data_label="ERBFile"):
        self.data_label = data_label
        self.funcs = FuncInfo()
        self.gotos = dict() # {cnt:label | label:lines}

    def code_checker(self, line:str):
        """받은 line의 코드 세부사항 분석 후 (int, int, int) 형태로 출력

        index 0(c_type): 0=기타 1=IF 2=CASE 3=PRINTDATA 4=반복문
        index 1(c_info): 0=단독 1=시작 2=중간 3=탈출
        index 2(c_etc): 세부내역 구분용
        """
        if line.startswith('PRINT'):
            if line.startswith('PRINTDATA'):
                return (3, 1, 0)
            elif line.startswith('PRINTBUTTON'):
                return (0, 0, 1)
            return (0, 0, 0)
        elif line.startswith(';'):
            return (None, None, None)  # 주석은 미처리
        # 조건문 처리
        elif line.startswith('IF'):
            return (1, 1, 0)
        elif line.startswith('ELSE'):
            if line.startswith('ELSEIF'):  # 다항조건문의 1 ~ -2 번째 항
                return (1, 2, 0)
            else:  # 다항조건문의 -1항
                return (1, 2, 1)
        elif line.startswith('SIF'):  # 한줄짜리 IF문. 탈출자 없음
            return (1, 0, 0)
        elif line.startswith('ENDIF'):  # 탈출자
            return (1, 3, 0)
        # 분기문 처리
        elif line.startswith('CASE'):
            if line.startswith('CASEELSE'):
                return (2, 2, 1)
            return (2, 2, 0)
        elif line.startswith('SELECTCASE'):
            return (2, 1, 0)
        elif line.startswith('END'):
            if line.startswith('ENDLIST'):
                return (3, 3, 1)
            elif line.startswith('ENDDATA'):
                return (3, 3, 0)
            elif line.startswith('ENDSELECT'):
                return (2, 3, 0)
        elif line.startswith('DATA'):
            if line.startswith('DATAFORM'):
                return (3, 0, 0)
            elif line.startswith('DATALIST'):
                return (3, 1, 1)
            return (3, 0, 0)
        # 반복문 처리
        elif line.startswith('FOR'):
            return (4, 1, 0)
        elif line.startswith('REPEAT'):
            return (4, 1, 1)
        elif line.startswith('WHILE'):
            return (4, 1, 2)
        elif line.startswith('NEXT'):
            return (4, 3, 0)
        elif line.startswith('REND'):
            return (4, 3, 1)
        elif line.startswith('WEND'):
            return (4, 3, 2)
        elif line.startswith('BREAK'):
            return (4, 2, 0)
        elif line.startswith('CONTINUE'):
            return (4, 2, 1)
        # 기타 처리
        elif line.startswith('@'):
            return (0, 1, 0)
        elif line.startswith('$'): # GOTO LABEL
            return (0, 1, 1)
        elif line.startswith('{'):
            return (0, 1, 2)
        elif line.startswith('}'):
            return (0, 3, 2)
        elif line.startswith('GOTO'):
            return (0, 2, 0)
        elif line.startswith('CALL'):
            return (0, 2, 1)
        elif line.startswith('BEGIN'):
            return (0, 2, 2)
        elif line.startswith('#'): # DIM, FUNCTION 등 특수 코드
            return (0, 2, 3)
        elif line.startswith('RETURN'):  # RETURNF 도 인식함
            return (0, 3, 0)  # 함수 탈출자
        else:  # 일반문
            if line:
                return (0, 0, 2)
            return (None, None, None)  # 단순 빈줄 미처리

    def warp_func(self, s_lines:dict[int, str], s_indexs:list[int]):
        """self.funcs에 처리된 함수 저장"""
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

    def warp_goto(self, s_lines:dict[int, str], goto_head:int, cnt:int):
        """self.gotos에 처리된 goto문 저장, is_goto값 반환"""
        t_lines = [s_lines.get(i) for i in range(goto_head, cnt)]
        label = t_lines.pop(0)
        self.gotos[label] = t_lines
        return 0

    def warp_squash(self, checker:tuple, s_lines:dict[int, str], s_index:list[int], cnt):
        """{} 꼴 묶음 처리 함수. is_squash 값 반환"""
        if checker == (0, 3, 2): # }
            head_index = s_index.pop()
            temp_lines = []
            for num in range(cnt - head_index):
                temp_lines.append(s_lines.pop(cnt - num))
            s_lines[head_index] = temp_lines
            return False
        return True
    
    def warp_sif(self, s_lines:dict[int, str], s_index:list[int], cnt):
        """sif문 처리용 함수. is_sif값 반환"""
        head_index = s_index.pop()
        s_lines[head_index] = [s_lines[head_index], s_lines.pop(cnt)]
        return False

    def skip_line(self, line:str, switch:int):
        """주석 등 SKIP문 처리 코드블럭
        
        return 0:처리없음 1:SKIP 시작 2:SKIP 진행중 -1:SKIP 종료 -2:주석문
        """
        if line.startswith("[SKIPSTART]"):
            return 1
        elif line.startswith("[SKIPEND]"):
            return -1
        elif switch:
            return 2
        elif line.startswith(';'):
            return -2
        return 0

    def check_lines(self, lines:list[str]):
        """list[str] 기반 코드 블럭 분석 함수. 처리 과정은 stack 자료구조를 차용함.
        분석 자료는 self.funcs self.gotos 로 별도 관리됨.

        return : 비정상/상정외 작동의 경우 아이템이 남아있는 dict 형태 반환함, 정상인 경우 빈 dict
        """
        is_skip, is_goto, is_squash, is_sif = 0, 0, False, False
        stack_index = list()  # len()을 code 깊이 체크용으로 사용
        stack_goto = list()
        stack_lines = dict()

        for cnt, line in enumerate(lines):
            line = line.strip()
            # 주석문 통과 선처리
            is_skip = self.skip_line(line, is_skip)
            if is_skip:
                if is_skip <= -1:
                    is_skip = 0
                continue

            if not line: continue  # 공란은 통과

            checker = self.code_checker(line)
            codetype, codeinfo, codeetc = checker
            stack_lines[cnt] = line

            if is_squash:
                is_squash = self.warp_squash(checker, stack_lines, stack_index, cnt)
            elif is_sif:
                is_sif = self.warp_sif(stack_lines, stack_index, cnt)
            elif not codetype:
                if not codeinfo:
                    if codeetc == 2:  #TODO 특수 구문이 포함된 line
                        pass
                elif checker[1:] == (3, 0):  # RETURN
                    if len(stack_index) == 1:
                        self.warp_func(stack_lines, stack_index)
                elif checker[1:] == (1, 0):  # 함수 선언문
                    if stack_index:  # RETURN으로 끝나지 않은 함수가 있을때
                        if is_goto and len(stack_index) == 2:
                            is_goto = self.warp_goto(stack_lines, stack_goto.pop(), cnt)
                        self.warp_func(stack_lines, stack_index)
                    stack_index.append(cnt)
                    is_goto = 0
                elif checker[1:] == (1, 1):  # GOTO 시작점
                    if is_goto:  # GOTO 중첩 방지
                        is_goto = self.warp_goto(stack_lines, stack_goto.pop(), cnt)
                    is_goto = len(stack_index)
                    stack_goto.append(cnt)
                elif checker[1:] == (1, 2):  # {
                    stack_index.append(cnt)
                    is_squash = True
                elif checker[1:] == (2, 0):  # GOTO 호출
                    self.gotos[cnt] = line.split(" ")[-1]  # GOTO Label명
                    if is_goto == len(stack_index):
                        is_goto = 0

            elif codeinfo == 0:
                if codetype == 1:  # SIF
                    stack_index.append(cnt)
                    is_sif = 1
            # 블럭 시작
            elif codeinfo == 1:
                stack_index.append(cnt)
            # 블럭 내 분기
            elif codeinfo == 2:
                pass  #TODO
            # 블럭 탈출
            elif codeinfo == 3:
                start_index = stack_index.pop()
                temp_lines = []
                key = cnt
                while key != start_index:
                    key, val = stack_lines.popitem()
                    temp_lines.insert(0, val)
                stack_lines[start_index] = temp_lines
            else:
                raise NotImplementedError(line)

            # goto 블럭 종료 여부 처리
            if is_goto >= len(stack_index):
                is_goto = self.warp_goto(stack_lines, stack_goto.pop(), cnt)

        # RETURN 없는 함수 정리
        if stack_index:
            if is_goto and len(stack_index) == 2:
                is_goto = self.warp_goto(stack_lines, stack_goto.pop(), cnt)
            self.warp_func(stack_lines, stack_index)

        return stack_lines


class MetaERB(CheckStack):
    """ERB 파일 메타정보 처리 클래스.

    Functions:
        build_metalines(lines, mod_no)
        fix_grammar(erbinfos, mod_no)
    Variables:
        data_label
    """

    def __init__(self, data_label="MetaERB"):
        super().__init__(data_label)

    def build_metalines(self, lines:list[str], mod_no=0b00):
        """ERBInfo형 데이터 작성 함수. [if단계, case단계, 분기갯수, 원문] 꼴
        
        mod_no  0        1
        bit 0   전부     출력문 제외
        bit 1   기본값   case_count 주석 포함
        """
        is_skip, is_goto, is_squash, is_sif, is_datalist = 0, 0, False, False, False
        stack_indexs = {0:[], 1:[], 2:[], 3:[], 4:[]}  # {codetype:[]}
        total_lv = lambda x, i, c: sum([len(val) for val in x.values()]) + i + c
        cur_case = 0  # codetype
        case_count = dict()  # {head_cnt:count}, if/case 공용
        stack_lines = dict()  # {cnt:line}
        erb_infos = ERBInfo(lines)
        
        for cnt, line in enumerate(lines):
            tmp_if, tmp_case = 0, 0  # 해당 line에만 한정된 lv 변화
            blk_head, f_count = -1, 0  # blk_head: blk 종료시 시작 index 체크 f_count: 케이스 종료시 갯수 처리
            line = line.strip()
            # 주석문 통과 선처리
            is_skip = self.skip_line(line, is_skip)
            if is_skip:
                if is_skip <= -1:
                    is_skip = 0
                continue

            if not line: continue  # 공란은 통과

            checker = self.code_checker(line)
            codetype, codeinfo, codeetc = checker
            stack_lines[cnt] = line

            if is_squash:
                s_indexs = stack_indexs[codetype]
                is_squash = self.warp_squash(checker, stack_lines, s_indexs, cnt)
                stack_indexs[codetype] = s_indexs
                if not is_squash:
                    stack_indexs[codetype] = s_indexs
            elif is_sif:
                s_indexs = stack_indexs[1]
                is_sif = self.warp_sif(stack_lines, s_indexs, cnt)
                stack_indexs[1] = s_indexs
                tmp_if += 1
            elif codetype == 0:
                if codeinfo == 0 and mod_no & 0b1:  # PRINT, PRINTBUTTON
                    continue
                elif codeinfo == 1:
                    if codeetc == 0 and stack_indexs[0]:  # @(함수)
                        if is_goto and len(stack_indexs[0]) == 2:
                            is_goto = self.warp_goto(stack_lines, stack_indexs[0].pop(), cnt)
                        self.warp_func(stack_lines, stack_indexs[0])
                    elif codeetc == 1:  # $(GOTO)
                        if is_goto:
                            self.warp_goto(stack_lines, stack_indexs[0].pop(), cnt)
                        is_goto = total_lv(stack_indexs, tmp_if, tmp_case)
                    elif codeetc == 2:  # {
                        is_squash = 1
                    stack_indexs[codetype].append(cnt)
                elif checker[1:] == (3, 0):  # RETURN
                    if is_goto >= total_lv(stack_indexs, tmp_if, tmp_case):
                        is_goto = self.warp_goto(stack_lines, stack_indexs[0].pop(), cnt)
            elif codeinfo == 1 and codetype in (1,2,3,4):
                stack_indexs[codetype].append(cnt)
                cur_case = codetype
                if checker != (3, 1, 1):
                    case_count[cnt] = 1 if codetype == 1 else 0
                    tmp_if, tmp_case = (-1, 0) if codetype in (1, 4) else (0, -1)
                else:  # DATALIST
                    case_count[stack_indexs[codetype][-2]] += 1
                    is_datalist = 1
            elif codeinfo == 3 and codetype in (1,2,3,4):
                blk_head = stack_indexs[codetype].pop()
                if not len(stack_indexs[codetype]):
                    cur_case = 0
                if checker == (3, 3, 1):  # ENDLIST
                    is_datalist = 0
            elif codetype == 1:  # IF문
                tmp_if -= 1
                if codeinfo == 2:  # ELSEIF, ELSE
                    case_count[stack_indexs[codetype][-1]] += 1
                elif codeinfo == 0:  # SIF
                    stack_indexs[codetype].append(cnt)
                    is_sif = True
            elif checker[:2] == (2, 2):  # CASE, CASEELSE
                case_count[stack_indexs[codetype][-1]] += 1
                tmp_case -= 1
            elif checker == (3, 0, 0):  # DATA, DATAFORM
                if not is_datalist: # DATALIST 안 구문이 아닐 때 
                    case_count[stack_indexs[codetype][-1]] += 1
                else:
                    tmp_case += 1
                if mod_no & 0b1: continue

            if blk_head >= 0:  # pop() 통한 블럭 종료 감지
                if checker == (3, 3, 1):  # ENDLIST
                    f_count = 0
                else:
                    f_count = case_count.pop(blk_head) if isinstance(case_count.get(blk_head), int) else 0
                    if mod_no & 0b10 and codetype != 4:
                        line = line + " ;{}개의 케이스 존재".format(f_count)
            else:
                f_count = case_count.get(stack_indexs[cur_case][-1])
                if f_count == None: f_count = 0

            if is_goto >= total_lv(stack_indexs, tmp_if, tmp_case):
                is_goto = self.warp_goto(stack_lines, stack_indexs[0].pop(), cnt)
            
            erb_infos.add_row(
                len(stack_indexs[1] + stack_indexs[4]) + tmp_if,
                len(stack_indexs[2] + stack_indexs[3]) + tmp_case,
                f_count, line)
            # 분기문 블럭 내부가 아닌 RETURN, f_count와의 충돌 방지 위해 후처리함
            if checker == (0, 3, 0) and total_lv(stack_indexs, tmp_if, tmp_case) == 1:
                self.warp_func(stack_lines, stack_indexs[0])

        if stack_indexs[0]:  # RETURN 없는 함수 정리
            if is_goto and len(stack_indexs[0]) == 2:
                is_goto = self.warp_goto(stack_lines, stack_indexs[0].pop(), cnt)
            self.warp_func(stack_lines, stack_indexs[0])
        return erb_infos

    def fix_grammar(self, erbinfos: ERBInfo, mod_no=0):
        """ERBMetaInfo 기반 문법 교정기

        mod_no = bit 1: 중첩 printdata문 처리 on/off
        """
        result_lines:list[str] = []
        change_dict:dict[int, str] = {}
        ch_printdata = 0

        for count, line in enumerate(erbinfos.m_lines()):
            _, _, case_count, context = line
            if context.startswith('PRINTDATA'):
                ch_printdata += 1
                if mod_no & 0b1 and ch_printdata > 1:
                    change_dict[count] = 'fix_printdata/'
            elif mod_no & 0b1 and ch_printdata > 1:
                head_word = context.split()[0]
                if context.startswith('ENDDATA'):
                    ch_printdata -= 1
                    change_dict[count] = 'fix_enddata/'
                elif context.startswith('DATA'):
                    if head_word == 'DATALIST':
                        change_dict[count] = 'fix_datalist/'
                    elif head_word in ('DATAFORM','DATA'):
                        if case_count:
                            change_dict[count] = 'fix_data/fix_datalist/'
                        else:
                            change_dict[count] = 'fix_data/'
                    else:
                        print("상정하지 않은 케이스 :" + context)
                elif context.startswith('ENDLIST'):
                    change_dict[count] = 'delete'
            elif context.startswith('ENDDATA'):
                ch_printdata -= 1
            result_lines.append(line)

        keys = list(change_dict.keys())
        if not keys:
            return erbinfos
        else:
            print("{}에서 문법 교정을 시도합니다.".format(self.data_label))
        keys.sort(reverse=True)

        case_cntdict = {}
        for key in keys:
            value = change_dict[key]
            if value == 'delete':
                result_lines.pop(key)
            elif 'fix' in value:
                target_line:tuple[int, int, int, str] = result_lines[key]
                _, case_lv, case_count, context = target_line
                res_context = ''
                if  mod_no & 0b1 and 'data' in value:
                    if "fix_data/" in value:
                        res_context += context.replace(context.split()[0], 'PRINTFORMW')
                        value = value.replace("fix_data/", '')
                        if 'fix_datalist/' in value:
                            context = 'DATALIST'
                    if 'fix_datalist/' in value:
                        no = case_count
                        if_sent = "ELSEIF A == %d" % (no - 1)
                        if no == 1:
                            if_sent = if_sent.replace('ELSEIF', 'IF')
                        res_context += context.replace('DATALIST', if_sent)
                    elif value == 'fix_printdata/':
                        res_context += "A = RAND:%d" % case_cntdict.pop(case_lv)
                    elif value == 'fix_enddata/':
                        total_count = result_lines[key-1][2]
                        case_cntdict[case_lv] = total_count
                        res_context += context.replace('ENDDATA', 'ENDIF')
                    elif value == '':
                        pass
                    else:
                        print("상정외 value :" + value)
                        res_context = context
                    
                    post_context = ''
                    if 'IF' in res_context and 'PRINTFORMW' in res_context:
                        res_context, post_context = res_context.split('IF')
                        if 'ELSE' in res_context:
                            res_context = res_context.replace('ELSE', '')
                            post_context = 'ELSEIF' + post_context
                        else:
                            post_context = 'IF' + post_context
                    target_line[-1] = res_context
                    result_lines[key] = target_line
                    if post_context:
                        post_line = target_line.copy()
                        post_line[-1] = post_context
                        result_lines.insert(key, post_line)
        for cnt, metaline in enumerate(result_lines):
            erbinfos.df.loc[cnt] = metaline
        erbinfos.df['f_line'] = erbinfos.df['line']
        return erbinfos


class sample_code:
    def __init__(self, target_filename=None):
        if not target_filename:
            target_filename = input("Input File Name : ")
        self.open_gen = open(target_filename, 'r', encoding='utf-8-sig')

    def gen_bulk(self):
        with self.open_gen:
            result_lines = self.open_gen.readlines()
        return result_lines


if __name__ == '__main__':
    sample = sample_code()
    tester = CheckStack("test_file")
    a = tester.check_lines(sample.gen_bulk())
    print(tester.funcs.func_dict())
    input(a)
