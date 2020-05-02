import sys

from ply.lex import LexError
from lexerClass import MyLexer
import ply.yacc as yacc
from typing import List, Optional


class SyntaxTreeNode:
    def __init__(self, node_type, value=None, children=None, lineno=None, lexpos=None):
        self.type = node_type
        self.value = value
        self.children = children
        self.lineno = lineno
        self.lexpos = lexpos

    def __repr__(self):
        return f'''{self.type} {self.value} {self.lineno} : {self.lexpos}'''

    def print(self, level: int = 0):
        if self is None:
            return
        print(' ' * level, self)
        if isinstance(self.children, SyntaxTreeNode):
            self.children.print(level + 1)
        elif isinstance(self.children, list):
            for i in range(len(self.children)):
                self.children[i].print(level + 1)
        elif isinstance(self.children, dict):
            for key, value in self.children.items():
                print(' ' * (level + 1), key)
                if value:
                    value.print(level + 2)


class MyParser(object):
    tokens = MyLexer.tokens

    def __init__(self):
        self.lexer = MyLexer()
        self.parser = yacc.yacc(module=self)
        self.functions = dict()

    def p_program(self, p):
        """program : stmt_list"""
        p[0] = SyntaxTreeNode('program', children=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def parse(self, s):
        try:
            res = self.parser.parse(s)
            return res, self.functions
        except LexError:
            sys.stderr.write(f'Illegal token {s}\n', s)

    def p_stmt_list(self, p):
        """stmt_list : stmt_list statement
                    | statement"""
        if len(p) == 2:
            p[0] = SyntaxTreeNode('stmt_list', children=[p[1]])
        else:
            p[0] = SyntaxTreeNode('stmt_list', children=[p[1], p[2]])

    def p_statement(self, p):
        """statement : declaration NL
                    | assignment NL
                    | for NL
                    | if NL
                    | operation NL
                    | function NL
                    | function_call NL"""
        p[0] = p[1]

    def p_declaration(self, p):
        """declaration : type VARIABLE EQ expression
                       | type VARIABLE EQ L_FIGBRACKET decl_list R_FIGBRACKET"""
        if len(p) == 5:
            p[0] = SyntaxTreeNode('declaration', value=p[1],
                                  children=[SyntaxTreeNode('ident', value=p[2], lineno=p.lineno(2), lexpos=p.lexpos(2)),
                                            p[4]], lineno=p.lineno(2), lexpos=p.lexpos(2))
        else:
            p[0] = SyntaxTreeNode('declaration', value=p[1],
                                  children=[SyntaxTreeNode('ident', value=p[2], lineno=p.lineno(2), lexpos=p.lexpos(2)),
                                            p[5], SyntaxTreeNode('end_of_list')], lineno=p.lineno(2), lexpos=p.lexpos(2))

    def p_decl_list(self, p):
        """decl_list : L_FIGBRACKET expr_list R_FIGBRACKET
                     | decl_list COMMA L_FIGBRACKET decl_list R_FIGBRACKET
                     | expr_list"""
        if len(p) == 4:
            p[0] = SyntaxTreeNode('decl_list', children=[p[2],  SyntaxTreeNode('end_of_list')])
        elif len(p) == 2:
            p[0] = SyntaxTreeNode('decl_list', children=[p[1], SyntaxTreeNode('end_of_list')])
        else:
            p[0] = SyntaxTreeNode('decl_list', children=[p[1], p[4]])

    def p_expr_list(self, p):
        """expr_list : expr_list COMMA expression
                     | expression"""
        if len(p) == 2:
            p[0] = SyntaxTreeNode('expr_list', children=[p[1]], lineno=p.lineno(1), lexpos=p.lexpos(1))
        else:
            p[0] = SyntaxTreeNode('expr_list', children=[p[1], p[3]], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_type(self, p):
        """type : int
                | bool"""
        p[0] = SyntaxTreeNode('type', value=p[1], children=[], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_int(self, p):
        """int : INT
               | CINT
               | VINT
               | MINT
               | CVINT
               | CMINT"""
        p[0] = p[1]

    def p_bool(self, p):
        """bool : BOOL
                | CBOOL
                | VBOOL
                | MBOOL
                | CVBOOL
                | CMBOOL"""
        p[0] = p[1]

    def p_expression(self, p):
        """expression : math_expression
                      | const
                      | variable"""
        p[0] = SyntaxTreeNode('expression', children=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_math_expression(self, p):
        """math_expression :  expression PLUS expression
                            | expression MINUS expression
                            | expression MUL_MATRIX expression
                            | expression MUL_ELEM expression
                            | expression TRANSPOSE
                            | SUM LBRACKET expression RBRACKET
                            | expression STL
                            | expression STR
                            | DENY expression
                            | expression AND expression
                            | expression LESS expression
                            | expression GREATER expression"""
        if len(p) == 3 and p[1] != '!':
            p[0] = SyntaxTreeNode('un_op', p[2], children=p[1], lineno=p.lineno(2), lexpos=p.lexpos(2))
        elif len(p) == 5:
            p[0] = SyntaxTreeNode('un_op', p[1], children=p[3], lineno=p.lineno(2), lexpos=p.lexpos(2))
        elif len(p) == 3 and p[1] == '!':
            p[0] = SyntaxTreeNode('un_op', p[1], children=p[2], lineno=p.lineno(2), lexpos=p.lexpos(2))
        else:
            p[0] = SyntaxTreeNode('bin_op', p[2], children=[p[1], p[3]], lineno=p.lineno(2), lexpos=p.lexpos(2))

    def p_const(self, p):
        """const : TRUE
                 | FALSE
                 | INT_DEC
                 | INT_BIN"""
        p[0] = SyntaxTreeNode('const', value=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_variable(self, p):
        """variable : VARIABLE
                    | VARIABLE LBRACKET index RBRACKET"""
        if len(p) == 2:
            p[0] = SyntaxTreeNode('variable', p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))
        else:
            p[0] = SyntaxTreeNode('indexing', p[1], children=p[3], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_ind_exp(self, p):
        """ind : COMMA
               | COMMA COLON
               | COLON COMMA"""
        if len(p) == 3 and p[1] == ':':
            p[0] = SyntaxTreeNode('colon', value=p[1])
        elif len(p) == 3 and p[2] == ':':
            p[0] = SyntaxTreeNode('colon', value=p[2])
        else:
            p[0] = SyntaxTreeNode('comma', value=p[1])

    def p_index(self, p):
        """index : expression
                 | expr_list
                 | expr_list ind
                 | ind expr_list
                 | decl_list ind
                 | ind decl_list
                 | decl_list"""
        if len(p) == 2:
            p[0] = SyntaxTreeNode('index', children=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))
        elif len(p) == 3 and (p[2].type == 'colon' or p[2].type == 'comma'):
            p[0] = SyntaxTreeNode('index', children=[p[1], p[2]], lineno=p.lineno(1), lexpos=p.lexpos(1))
        elif len(p) == 3 and (p[1].type == 'colon' or p[1].type == 'comma'):
            p[0] = SyntaxTreeNode('index', children=[p[1], p[2]], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_operation(self, p):
        """operation : MOVE LBRACKET math_expression RBRACKET
                     | RIGHT
                     | LEFT
                     | WALL
                     | EXIT"""
        if len(p) == 2:
            p[0] = SyntaxTreeNode('robot', value=p[1], children=[], lineno=p.lineno(1), lexpos=p.lexpos(1))
        else:
            p[0] = SyntaxTreeNode('robot', value=p[1], children=[p[3]], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_assignment(self, p):
        """assignment : variable ASSIGNMENT expression
                     | variable ASSIGNMENT L_FIGBRACKET decl_list R_FIGBRACKET"""
        if len(p) == 4:
            p[0] = SyntaxTreeNode('assignment', value=p[1], children=p[3], lineno=p.lineno(1), lexpos=p.lexpos(1))
        else:
            p[0] = SyntaxTreeNode('assignment', value=p[1], children=p[4], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_for(self, p):
        """for : FOR VARIABLE EQ expression COLON expression BEGINFOR NL stmt_list ENDFOR
               | FOR VARIABLE EQ expression COLON expression BEGIN NL stmt_list END"""
        p[0] = SyntaxTreeNode('for', children={'var': SyntaxTreeNode('variable', p[2], children=[]),
                                               'from': p[4], 'to': p[6], 'body': p[9]}, lineno=p.lineno(1),
                              lexpos=p.lexpos(1))

    def p_if(self, p):
        """if : IF math_expression BEGINIF NL stmt_list ENDIF
              | IF math_expression BEGIN NL stmt_list END"""
        p[0] = SyntaxTreeNode('if', children={'condition': p[2], 'body': p[5]}, lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_return_list(self, p):
        """return_list : return_list COMMA type VARIABLE
                        | type VARIABLE"""
        if len(p) == 3:
            p[0] = SyntaxTreeNode('return_list', children=[p[1], p[2]], lineno=p.lineno(1), lexpos=p.lexpos(1))
        else:
            p[0] = SyntaxTreeNode('return_list', children=[p[1], p[3], p[4]], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_func_list(self, p):
        """func_list : func_list COMMA func
                    | func"""
        if len(p) == 2:
            p[0] = SyntaxTreeNode('func_list', children=[p[1]])
        else:
            p[0] = SyntaxTreeNode('func_list', children=[p[1], p[3]])

    def p_func(self, p):
        """func : type VARIABLE
                | type VARIABLE EQ const"""
        if len(p) == 3:
            p[0] = SyntaxTreeNode('func', children=[p[1], p[2]])
        else:
            p[0] = SyntaxTreeNode('func', children=[p[1], p[2], p[4]])

    def p_call_list(self, p):
        """call_list : call_list COMMA expression
                    | expression"""
        if len(p) == 2:
            p[0] = SyntaxTreeNode('call_list', children=[p[1]])
        else:
            p[0] = SyntaxTreeNode('call_list', children=[p[1], p[3]])

    def p_function(self, p):
        """function : return_list EQ FUNCTION VARIABLE LBRACKET func_list RBRACKET BEGIN NL stmt_list END
                    | FUNCTION VARIABLE LBRACKET func_list RBRACKET BEGIN NL stmt_list END
                    | return_list EQ FUNCTION VARIABLE LBRACKET RBRACKET BEGIN NL stmt_list END
                    | FUNCTION VARIABLE LBRACKET RBRACKET BEGIN NL stmt_list END
                    | type VARIABLE EQ FUNCTION VARIABLE LBRACKET func_list RBRACKET BEGIN NL stmt_list END
                    | type VARIABLE EQ FUNCTION VARIABLE LBRACKET RBRACKET BEGIN NL stmt_list END"""
        if len(p) == 12 and p[5] == '(':
            self.functions[p[4]] = SyntaxTreeNode('function', children={'param': p[6], 'body': p[10], 'return': p[1]},
                                                  lineno=p.lineno(3), lexpos=p.lexpos(3))
            p[0] = SyntaxTreeNode('function_description', value=p[4], lineno=p.lineno(3), lexpos=p.lexpos(3))
        elif len(p) == 10:
            self.functions[p[2]] = SyntaxTreeNode('function', children={'param': p[4], 'body': p[8]},
                                                  lineno=p.lineno(3), lexpos=p.lexpos(3))
            p[0] = SyntaxTreeNode('function_description', value=p[2], lineno=p.lineno(3), lexpos=p.lexpos(3))
        elif len(p) == 11:
            self.functions[p[4]] = SyntaxTreeNode('function', children={'return': p[1], 'body': p[9]},
                                                  lineno=p.lineno(3), lexpos=p.lexpos(3))
            p[0] = SyntaxTreeNode('function_description', value=p[2], lineno=p.lineno(3), lexpos=p.lexpos(3))
        elif len(p) == 9:
            self.functions[p[2]] = SyntaxTreeNode('function', children={'body': p[7]},
                                                  lineno=p.lineno(3), lexpos=p.lexpos(3))
            p[0] = SyntaxTreeNode('function_description', value=p[2], lineno=p.lineno(1), lexpos=p.lexpos(3))
        elif len(p) == 13:
            self.functions[p[5]] = SyntaxTreeNode('function',
                                                  children={'body': p[11], 'param': p[8],
                                                            'return': SyntaxTreeNode('returnl_list',
                                                                                     children=[p[1], p[2]])},
                                                  lineno=p.lineno(3), lexpos=p.lexpos(3))
            p[0] = SyntaxTreeNode('function_description', value=p[5], lineno=p.lineno(3), lexpos=p.lexpos(3))
        elif len(p) == 12 and p[6] == '(':
            self.functions[p[5]] = SyntaxTreeNode('function', children={'body': p[10],
                                                                        'return': SyntaxTreeNode('returnl_list',
                                                                                                 children=[p[1],
                                                                                                           p[2]])},
                                                  lineno=p.lineno(3), lexpos=p.lexpos(3))
            p[0] = SyntaxTreeNode('function_description', value=p[5], lineno=p.lineno(3), lexpos=p.lexpos(3))

    def p_function_call(self, p):
        """function_call : VARIABLE
                         | VARIABLE call_list
                         | ret_list ASSIGNMENT VARIABLE call_list
                         | ret_list ASSIGNMENT VARIABLE
                         | variable ASSIGNMENT VARIABLE call_list"""
        if len(p) == 2:
            p[0] = SyntaxTreeNode('function_call', value=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))
        elif len(p) == 3:
            p[0] = SyntaxTreeNode('function_call', value=p[1], children={'call': p[2]}, lineno=p.lineno(1), lexpos=p.lexpos(1))
        elif len(p) == 4:
            p[0] = SyntaxTreeNode('function_call', value=p[3], children={'return': p[1]}, lineno=p.lineno(2), lexpos=p.lexpos(2))
        elif len(p) == 5:
            p[0] = SyntaxTreeNode('function_call', value=p[3], children={'return': p[1], 'call': p[4]}, lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_ret_list(self, p):
        """ret_list : variable
                    | ret_list COMMA variable"""
        if len(p) == 2:
            p[0] = SyntaxTreeNode('ret_list', children=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))
        elif len(p) == 4:
            p[0] = SyntaxTreeNode('ret_list', children=[p[1], p[3]], lineno=p.lineno(3), lexpos=p.lexpos(3))

    def p_error(self, p):
        print(f'Syntax error at {p}')
        self.acc = False


if __name__ == '__main__':
    parser = MyParser()
    f = open('t1.txt', 'r')
    txt = f.read()
    f.close()
    print(f'INPUT: {txt}')
    tree, func_table = parser.parse(txt)
    # tree = parser.parser.parse(txt, debug=True)
    tree.print()