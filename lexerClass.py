import sys

import ply.lex as lex

reserved = {
    'if': 'IF', 'for': 'FOR', 'and': 'AND', 'sum': 'SUM', 'begin': 'BEGIN', 'end': 'END', 'beginfor': 'BEGINFOR',
    'endfor': 'ENDFOR', 'beginif': 'BEGINIF', 'endif': 'ENDIF', 'true': 'TRUE', 'false': 'FALSE', 'int': 'INT',
    'bool': 'BOOL', 'function': 'FUNCTION', 'move': 'MOVE', 'exit': 'EXIT', 'right': 'RIGHT', 'left': 'LEFT',
    'wall': 'WALL', 'cint': 'CINT', 'vint': 'VINT', 'cvint': 'CVINT', 'mint': 'MINT', 'cmint': 'CMINT',
    'cbool': 'CBOOL', 'vbool': 'VBOOL', 'cvbool': 'CVBOOL', 'mbool': 'MBOOL', 'cmbool': 'CMBOOL'
}


class MyLexer(object):

    def __init__(self):
        self.lexer = lex.lex(module=self)

    tokens = ['INT_DEC', 'INT_BIN', 'ASSIGMENT', 'PLUS', 'MINUS', 'VARIABLE', 'LBRACKET', 'RBRACKET',
              'MUL_MATRIX', 'MUL_ELEM', 'COLON', 'TRANSPOSE', 'STL', 'STR', 'DENY',
              'LESS', 'GREATER', 'EQ', 'R_FIGBRACKET', 'L_FIGBRACKET',
              'COMMA', 'NL'] + list(reserved.values())

    t_ASSIGMENT = r'\<\-'
    t_AND = r'&&'
    t_STL = r'\<\<'
    t_STR = r'\>\>'
    t_MUL_ELEM = r'\.\*'
    t_MUL_MATRIX = r'\*'
    t_PLUS = r'\+'
    t_LBRACKET = r'\('
    t_RBRACKET = r'\)'
    t_COLON = r'\:'
    t_TRANSPOSE = r'\''
    t_DENY = r'\!'
    t_LESS = r'\<'
    t_GREATER = r'\>'
    t_EQ = r'\='
    t_MINUS = r'\-'
    t_L_FIGBRACKET = r'\{'
    t_R_FIGBRACKET = r'\}'
    t_COMMA = r'\,'

    def t_VARIABLE(self, t):
        r'[a-zA-Z][a-zA-Z_0-9]*'
        t.type = reserved.get(t.value, 'VARIABLE')
        return t

    def t_INT_BIN(self, t):
        r'0[01]+'
        t.value = self.bit_to_dex(t.value)
        return t

    def t_INT_DEC(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    def t_NL(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        return t

    def t_CONTINUE(self, t):
        r'\.\.\.\n'
        t.lexer.lineno += len(t.value)-3
        pass

    def t_error(self, t):
        sys.stderr.write(f'Illegal character: {t.value[0]} at line {t.lexer.lineno}\n')
        t.lexer.skip(1)

    t_ignore = ' \t'

    def input(self, data):
        return self.lexer.input(data)

    def token(self):
        return self.lexer.token()

    def bit_to_dex(self, number):
        n = []
        for i in range(len(number)):
            n.append(number[i])
        del n[0]
        n.reverse()
        result = 0
        for index in range(len(n)):
            result += 2**index*int(n[index])
        return result


if __name__ == '__main__':
    f = open('testparser.txt')
    data = f.read()
    f.close()
    lexer = MyLexer()
    lexer.input(data)
    while True:
        token = lexer.token()
        if token is None:
            break
        else:
            print(token)

