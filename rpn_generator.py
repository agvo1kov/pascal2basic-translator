import pprint
from colorama import Fore, Back, Style

service_words = ['program', 'var', 'const', 'integer', 'real', 'string', 'label',
                 'array', 'of', 'procedure', 'function',
                 'begin', ':=', 'goto', 'if', 'then', 'else', 'end', 'end.', 'for', 'to', 'while', 'do']
operations = ['+', '-', '*', '/', '^', '<', '>', '=', '<>', '<=', '>=']
separators = [' ', ',', '..', ':', ';', '(', ')', '[', ']', '{', '}', '\'']

priority = dict(
    [('W10', 0), ('W14', 0), ('R5', 0), ('R7', 0), ('АЭМ', 0), ('W1', 0), ('W7', 0), ('W19', 0), ('W20', 0), ('W21', 0),
      ('КЦД', 0),
     ('R1', 1), ('R4', 1), ('R6', 1), ('R8', 1), ('W15', 1), ('W16', 1), ('W22', 1),
     ('W12', 2), ('W13', 2),
     ('O5', 3), ('O6', 3), ('O7', 3), ('O8', 3), ('O9', 3), ('O10', 3), ('R2', 3),
     ('O0', 4), ('O1', 4),
     ('O2', 5), ('O3', 5),
     ('O4', 6),
     ('W9', 7), ('W17', 7), ('R3', 7), ('W18', 7)])

stack = []
out_line = ''
normal_line = ''
tempState = ''
lableStack = []


def to_rpn(line):
    flagAEM = flagF = flagBegin = flagVar = flagConst = flagProc = flagLocal = flagFunc = flag_arr_dcl = flagBeginLoop = flagLable  = False
    dcl3 = tempIf = procCounter = arrDcl = 1
    flagIf = flagFor = flagWhile = 0
    work_line = line.split(' ')
    global out_line, tempState, stack
    for index, word in enumerate(work_line):
        # out_line += ' $$' + str(dcl3) + '$$ '
        print('Pre-stack:', stack, 'ind', index, word, '\n')
        if word[0] == "I" or word[0] == "C" or word[0] == 'M':
            if flagLable:
                lableStack.append(word)
            # Здесь надо проверять не I и C, а массив меток, но у меня его нет))
            if word[0] == 'M' and stack and stack[len(stack) - 1] == 'W13':
                out_line += word + ' БП '
                stack.pop()
            else:
                if out_line != '' and out_line[len(out_line) - 1] != ' ':
                    out_line += ' ' + word + ' '
                else:
                    out_line += word + ' '
        # R4 в случае закрытия условного оператора добавляет метку, иначе просто выталкивает все операторы
        elif word == 'R4':
            if flagFor == 2 and not flagBeginLoop:
                while stack and not stack[len(stack) - 1] == 'КЦД':
                    out_line += stack.pop() + ' '
                out_line += stack.pop() + ' '
                flagFor = 0
                flagBeginLoop = False
            if flagWhile == 2 and not flagBegin:
                while stack and not stack[len(stack) - 1] == 'КЦП':
                    out_line += stack.pop() + ' '
                out_line += stack.pop() + ' '
                flagWhile = 0
                flagBeginLoop = False
            if flagProc:
                out_line += str(procCounter) + ' ' + 'НП '
                stack.pop()
                flagProc = False
            elif flagVar:
                # out_line += ' $$' + str(dcl3) + '$$ '
                if dcl3 > 1:
                    out_line += str(dcl3) + ' ' + stack.pop() + ' '
                    dcl3 = 1
                else:
                    out_line += stack.pop() + ' '
            elif not flagBegin and flagIf == 'W16':  # Нет begin блок then
                while stack and not stack[len(stack) - 1] == 'W14':
                    out_line += stack.pop() + ' '
                if stack:
                    stack.pop()
                out_line += 'M' + str(tempIf) + ' R3 '
            elif flagLable:
                flagLable = False
                out_line += stack.pop() + ' '
            else:
                while stack and priority.get(word) <= priority.get(stack[len(stack) - 1], 0):
                    out_line += stack.pop() + ' '
        elif word == 'W1':
            stack.append(word)
            flagVar = True
        elif flagFor == 1 and word == 'W12':
            0
        elif word == 'W20':
            0
        elif word == 'R3':
            if tempState == 'R6':
                flagFunc = True
            if lableStack.__contains__(
                    out_line[0: len(out_line) - 1].split(' ')[len(out_line[0: len(out_line) - 1].split(' ')) - 1]):
                out_line += word + ' '
        elif word == 'W3' or word == 'W4' or word == 'W5':
            if flagFunc:
                out_line += word + ' '
                flagFunc = False
            else:
                stack.append(word)
        elif word == 'W9' or word == 'W10':
            # if word == 'W9':  # Procedure
            flagProc = True
            stack.append('W9')
            procCounter += 1
        # Встречаем условие
        elif word == 'W14':
            stack.append(word)
        elif word == 'W15':
            flagIf = 'W15'
            while not stack[len(stack) - 1] == 'W14':
                out_line += stack.pop() + ' '
            # if stack:
            #     stack.pop()
            out_line += 'M' + str(tempIf) + ' ' + 'УПЛ '
        elif word == 'W16':
            flagIf = 'W16'
            while not stack[len(stack) - 1] == 'W14':
                out_line += stack.pop() + ' '
            if stack:
                stack.pop()
            tempIf += 1
            out_line += 'M' + str(tempIf) + ' БП ' + 'M' + str(tempIf - 1) + ' R3 '
        elif word == 'W17':
            if flagIf == 'W16' or flagIf =='W15':
                while not stack[len(stack) - 1] == 'W14':
                    out_line += stack.pop() + ' '
                stack.pop()
                out_line += 'M' + str(tempIf) + ' R3 '
            if flagFor == 2:
                while stack and not stack[len(stack) - 1] == 'КЦД':
                    out_line += stack.pop() + ' '
                out_line += stack.pop() + ' '
                flagFor = 0
            if flagWhile == 2:
                while stack and not stack[len(stack) - 1] == 'КЦП':
                    out_line += stack.pop() + ' '
                out_line += stack.pop() + ' '
                flagWhile = 0
            flagFor = 0
            flagBegin = not flagBegin
            flagIf = 'R17'
        # Открывающая скобка, если это не функция, заносится в стек,
        # если функция - оператор Ф со значением счетчика 1
        # TODO: изменить, ибо не работает, если строка не с Ф начинается
        elif word == 'R5':
            if flagProc:
                out_line += str(procCounter) + ' ' + 'НП '
                stack.append(word)
                flagVar = True
            else:
                stack.append(word)
        # Закрывающая скобка выталкивает все операторы из стека, если встречается оператор Ф, то наращивается
        # его счетчик и они выталкиваются, если встретился оператор R5, то они самоликвидируются
        elif word == 'R6':
            if flagF:
                while not stack[len(stack) - 1] == 'Ф':
                    out_line += stack.pop() + ' '
                tempF += 1
                out_line += str(tempF) + stack.pop() + ' '
                flagF = False
            elif flagProc:
                while not stack[len(stack) - 1] == 'R5':
                    out_line += stack.pop() + ' '
                if dcl3 > 1:
                    out_line += str(dcl3) + ' ' + 'PAR '
                    dcl3 = 1
                else:
                    out_line += 'PAR'
                stack.pop()
                flagVar = False
            else:
                while not stack[len(stack) - 1] == 'R5':
                    out_line += stack.pop() + ' '
                stack.pop()
        # Открывающаяся фигурная скобка добавляет в стэк оператор АЭМ со значением счетчика 2
        elif word == 'R7':
            if not flagVar:
                stack.append('АЭМ')
                tempAEM = 2
                flagAEM = True
            else:
                0
        elif word == 'W7':
            stack.append('ARDCL')
            flag_arr_dcl = True
        elif word == 'R2':
            arrDcl += 1
        # Запятая внутри квадратных скобок выталкивает все операторы из стека до АЭМ и увеличивает его счетчик
        elif word == 'R1':
            if flag_arr_dcl:
                arrDcl += 1
            if flagAEM:
                while not stack[len(stack) - 1] == 'АЭМ':
                    out_line += stack.pop() + ' '
                tempAEM += 1
            if flagF:
                while not stack[len(stack) - 1] == 'Ф':
                    out_line += stack.pop() + ' '
                tempF += 1
            if stack and (
                    stack[len(stack) - 1] == 'W3' or stack[len(stack) - 1] == 'W4' or stack[len(stack) - 1] == 'W5'):
                out_line += stack.pop() + ' '
            if flagLocal:
                out_line += stack.pop() + ' '
            if flagConst:
                constCounter += 1
        # Закрывающаяся квадратная скобка выталкивает все операторы из стека до АЭМ, увеличивает его счетчик,
        # после чего выталкивает сам оператор АЕМ с его счетчиком
        elif word == 'R8':
            if not flagVar:
                while not stack[len(stack) - 1] == 'АЭМ':
                    out_line += stack.pop() + ' '
                out_line += str(tempAEM) + ' ' + stack.pop() + ' '
                flagAEM = False
        elif word == 'W8':
            while not stack[len(stack) - 1] == 'ARDCL':
                out_line += stack.pop() + ' '
            arrDcl += 1
            out_line += str(arrDcl) + ' ' + stack.pop() + ' '
            flag_arr_dcl = False
            arrDcl = 1
        elif word == 'W11' or word == 'W2' or word == 'W6':
            if flagFor or flagWhile:
                flagBeginLoop = True
            if flagVar:
                while stack and not stack[len(stack) - 1] == 'W1':
                    out_line += stack.pop() + ' '
                out_line += str(procCounter) + ' ' + 'КО '
                stack.pop()
                flagVar = False
            if word == 'W6':
                flagLable = True
                stack.append(word)
            flagBegin = True
            proc3 = 1
            if (word == 'W2' or word == 'W6') and flagVar:
                flagVar = False
                flagConst = True
                constCounter = 1
        elif word == 'W18':
            out_line += word
        elif word == 'W19':
            flagFor = 1
            tempLoopCounter = 3
            stack.append('КЦД')
            stack.append('НЦД')  # Начало Цикла Для
        elif word == 'W21':
            flagWhile = 1
            tempLoopCounter = 2
            stack.append('КЦП')
            stack.append('НЦП')
        elif word == 'W22':
            if flagFor:
                while stack and not stack[len(stack) - 1] == 'НЦД':
                    out_line += stack.pop() + ' '
                out_line += str(tempLoopCounter) + ' ' + stack.pop() + ' '
                if flagFor == 1:
                    flagFor = 2
            if flagWhile:
                while stack and not stack[len(stack) - 1] == 'НЦП':
                    out_line += stack.pop() + ' '
                out_line += str(tempLoopCounter) + ' ' + stack.pop() + ' '
                if flagWhile == 1:
                    flagWhile = 2
        elif not stack:
            stack.append(word)
        # Если приоритет операции ниже, чем крайней операции в стеке, то он просто проталкивается в стек
        elif priority.get(word) > priority.get(stack[len(stack) - 1], 0):
            stack.append(word)
            if (flagFor or flagWhile) and (word == 'O0' or word == 'O1' or word == 'O2' or word == 'O3'):
                tempLoopCounter += 1
        # Если приоритет операции выше, чем крайней операции в стеке, то выталкиваются все операторы до тех пор,
        # пока не встретится оператор с таким же или выше приоритетом
        elif priority.get(word) <= priority.get(stack[len(stack) - 1], 0):
            while stack and priority.get(word) <= priority.get(stack[len(stack) - 1], 0):
                out_line += stack.pop() + ' '
            stack.append(word)
            if (flagFor or flagWhile) and (word == 'O0' or word == 'O1' or word == 'O2' or word == 'O3'):
                tempLoopCounter += 1
        tempState = word
    # Дописываются оставшиеся в стэке операторы
    while stack:
        out_line += stack.pop() + ' '
    print(out_line)
    return out_line

def to_normal(line):
    global normal_line
    line = line.split(' ')
    for word in line:
        if word[0] == 'I' or word[0]=='C':
            normal_line += word
        if str(word).isnumeric():
            normal_line += word
        if word == 'W0':
            normal_line += 'program'
        if word == 'W1':
            normal_line += 'var'
        if word == 'W2':
            normal_line += 'const'
        if word == 'W3':
            normal_line += 'integer'
        if word == 'W4':
            normal_line += 'real'
        if word == 'W5':
            normal_line += 'string'
        if word == 'W6':
            normal_line += 'label'
        if word == 'W7':
            normal_line += 'array'
        if word == 'W8':
            normal_line += 'of'
        if word == 'W9':
            normal_line += 'procedure'
        if word == 'W10':
            normal_line += 'function'
        if word == 'W11':
            normal_line += 'begin'
        if word == 'W12':
            normal_line += ':='
        if word == 'W13':
            normal_line += 'goto'
        if word == 'W14':
            normal_line += 'if'
        if word == 'W15':
            normal_line += 'then'
        if word == 'W16':
            normal_line += 'else'
        if word == 'W17':
            normal_line += 'end'
        if word == 'W18':
            normal_line += 'end.'
        if word == 'W19':
            normal_line += 'for'
        if word == 'W20':
            normal_line += 'to'
        if word == 'W21':
            normal_line += 'while'
        if word == 'W22':
            normal_line += 'do'
        if word == 'O0':
            normal_line += '+'
        if word == 'O1':
            normal_line += '-'
        if word == '02':
            normal_line += '*'
        if word == 'O3':
            normal_line += '/'
        if word == 'O4':
            normal_line += '^'
        if word == 'O5':
            normal_line += '<'
        if word == 'O6':
            normal_line += '>'
        if word == 'O7':
            normal_line += '='
        if word == 'O8':
            normal_line += '<>'
        if word == 'O9':
            normal_line += '<='
        if word == 'O10':
            normal_line += '>='
        if word == 'O11':
            normal_line += '<'
        if word == 'O12':
            normal_line += '>'
        if word == 'R0':
            normal_line += ' '
        if word == 'R1':
            normal_line += ','
        if word == 'R2':
            normal_line += '..'
        if word == 'R3':
            normal_line += ':'
        if word == 'R4':
            normal_line += ';'
        if word == 'R5':
            normal_line += '('
        if word == 'R6':
            normal_line += ')'
        if word == 'R7':
            normal_line += '['
        if word == 'R8':
            normal_line += ']'
        if word == 'R9':
            normal_line += '{'
        if word == 'R10':
            normal_line += '}'
        normal_line += ' '
    print(normal_line)


to_normal(to_rpn(
    'W1 I1 R1 I2 R3 W3 R4 I3 R3 W7 R7 C0 R2 C1 R1 C2 R2 C3 R8 W8 W3 R4 I4 R3 W7 R7 C0 '
    'R2 C4 R8 W8 W3 R4 I5 R3 W4 R4 I6 R1 I7 R3 W5 R4 W6 I8 R1 I9 R4 W11 W19 I1 W12 C0 O0 C5 W20 C1 W22 I1 W12 C2 O2 '
    'C3 R4 I2 W12 C4 O1 C5 R4 I1 W12 C5 R4 W12 R5 '
    'C6 O0 C7 R6 R4 I6 W12 I6 O0 C8 R4 I5 W12 C9 R4 I7 W12 C6 R4 I3 R7 C10 O0 C5 O1 C0 R1 C2 R8 W12 C2 O0 C3 R4 I8 R3 '
    'W14 R5 I1 O6 C2 O0 C0 R6 W15 W13 I9 W16 I1 W12 I1 O0 C0 R4 I2 W12 O1 C0 O2 C0 O1 C5 R4 I6 W12 C11 O0 C12 R4 W13 '
    'I8 R4 I5 W12 C13 R4 I9 R3 W18'))

# I1 I2 W3 I3 C0 C1 C2 C3 5 ARDCL W3 I4 C0 C4 3 ARDCL W3 I5 W4 I6 I7 W5 1 КО I8 I9 W6 I1 C5 W12 C6 C7 O0 W12 I6 I6 C8
# O0 W12 I5 C9 W12 I7 C6 W12 I3 C10 C5 O0 C0 O1 C2 3 АЭМ C2 C3 O0 W12 I8 R3 I1 C2 C0 O0 O6 M1 УПЛ I9 W13 M2 БП M1 R3 I1
# I1 C0 O0 W12 I2 C0 C0 O2 O1 C5 O1 W12 I6 C11 C12 O0 W12 I8 W13 I5 C13 W12 I9 R3 W18

# Тест индексов
# to_rpn('R5 I0 O0 I1 R7 I2 O0 C1 R1 I3 R8 R6 O2 R5 I4 O0 I5 R6')
# (I0 + I1[I2 + C1, I3]) - (I4 + I5)

# Тест функций
# to_rpn('I0 O1 I1 R5 I2 R1 I3 R1 I4 O0 C0 R6')

# Тест безусловных переходов
# to_rpn('I0 W12 I1 O0 I2 R4 W13 M1 R4 I3 W12 I4 O2 I5 O1 I6 R4 M1 R3')

# Тест begin ... end
# to_rpn('I0 W12 C3 O1 C4 R4 I1 W12 C5 O1 C6 R4')

# Тест условный операторов if ... else
# to_rpn('W14 C0 O5 C1 W15 I0 W12 C7 O0 C2 R4 W16 W11 I0 W12 C3 O1 C4 R4 I1 W12 C5 O1 C6 R4 W17 R4')
# Out: C0 C1 O5 M1 УПЛ I0 C7 C2 O0 W12 M2 БП M1 R3 I0 C3 C4 O1 W12 I1 C5 C6 O1 W12 M2 R3


# Тест условный оператор if
# to_rpn('W14 C0 O5 C1 W15 W11 I0 W12 C3 O1 C4 R4 I1 W12 C5 O1 C6 R4 W17')

# Тест цикла for
# to_rpn('W19 I0 W12 C0 O0 C5 W20 C1 W22 I1 W12 C2 O2 C3 R4 I2 W12 C4 O1 C5 R4')

# Тест цикла while
# to_rpn('W21 I0 O5 C0 O1 C6 W22 W11 I1 W12 C2 O2 C3 R4 I2 W12 C4 O1 C5 R4 W17')


# Тест var
# to_rpn('W1 I1 R1 I2 R3 W3 R4 I7 R3 W5 R4 W2 I3 O7 C2 R4 W9 I4 R5 I5 R3 W3 R1 I6 R3 W5 R6 R3 W5 R4 W11 W1 I10 R3 W5 R4 I11 R1 I12 R3 W3 R4 W11')
# Out: I1 I2 2 W3 I7 W5 КО I3 C2 O7 I4 I5 W3 I6 W5 2 PAR 1 1 НП I10 W5 I11 I12 2 W3 КО

