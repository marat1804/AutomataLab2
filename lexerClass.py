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

    tokens = ['INT_DEX', 'INT_BIN', 'ASSIGMENT', 'PLUS', 'MINUS', 'VARIABLE', 'LBRACKET', 'RBRACKET',
              'MUL_MATRIX', 'MUL_ELEM', 'COLON', 'TRANSPOSE', 'STL', 'STR', 'DENY', 'SPACE',
              'LESS', 'GREATER', 'EQ', 'R_FIGBRACKET', 'L_FIGBRACKET', 'CONTINUE', 'L_SQBRACKET', 'R_SQBRACKET',
              'COMMA'] + list(reserved.values())

    t_ASSIGMENT = r'\<\-'
    t_AND = r'&&'
    t_STL = r'\<\<'
    t_STR = r'\>\>'
    t_MUL_ELEM = r'\.\*'
    t_MUL_MATRIX = r'\*'
    t_PLUS = r'\+'
    t_LBRACKET = r'\('
    t_RBRACKET = r'\)'
    t_L_SQBRACKET = r'\['
    t_R_SQBRACKET = r'\]'
    t_COLON = r'\:'
    t_TRANSPOSE = r'\''
    t_DENY = r'\!'
    t_LESS = r'\<'
    t_GREATER = r'\>'
    t_EQ = r'\='
    t_MINUS = r'\-'
    t_L_FIGBRACKET = r'\{'
    t_R_FIGBRACKET = r'\}'
    t_CONTINUE = r'\.\.\.'
    t_COMMA = r'\,'

    def t_VARIABLE(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = reserved.get(t.value, 'VARIABLE')
        return t

    def t_INT_BIN(self, t):
        r'0[01]+'
        return t

    def t_INT_DEX(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])

    t_ignore = ' \t'

    def input(self, data):
        return self.lexer.input(data)

    def token(self):
        return self.lexer.token()


if __name__ == '__main__':
    f = open('test2.txt')
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
