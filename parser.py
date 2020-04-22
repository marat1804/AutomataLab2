import sys

from ply.lex import LexError
from lexerClass import MyLexer
import ply.yacc as yacc
from typing import List, Optional


class SyntaxTreeNode:
    def __init__(self, node_type, value=None, children: Optional[List] = None):
        self.type = node_type
        self.value = value
        self.children = children

    def __repr__(self):
        return f'''{self.type} {self.value}'''

    def print(self, level: int = 0):
        print(' ' * level, ' ', self)
        if self.children is not None:
            if isinstance(self.children, SyntaxTreeNode):
                self.children.print(level + 1)
            elif isinstance(self.children, str):
                print(' ' * (level + 1), self.children)
            elif isinstance(self.children, list):
                for i in range(len(self.children)):
                    if isinstance(self.children[i], str):
                        print(' ' * (level + 1), self.children[i])
                    else:
                        self.children[i].print(level + 1)
            elif isinstance(self.children, dict):
                for key, value in self.children.items():
                    print(' ' * (level + 1), key)
                    if isinstance(value, str):
                        print(' ' * (level + 2), value)
                    elif isinstance(value, SyntaxTreeNode):
                        value.print(level + 2)


class MyParser(object):
    tokens = MyLexer.tokens

    def __init__(self):
        self.lexer = MyLexer()
        self.parser = yacc.yacc(module=self)
        self.functions = dict()

    def p_program(self, p):
        """program : stmt_list"""
        p[0] = SyntaxTreeNode('program', children=p[1], value='prog')

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
            p[0] = SyntaxTreeNode('stmt_list', children=p[1])
        else:
            p[0] = SyntaxTreeNode('stmt_list', children=[p[1], p[2]])

    def p_statement(self, p):
        """statement : declaration NL
                    | assigment NL
                    | for NL
                    | if NL
                    | operation NL
                    | function NL
                    | function_call NL"""
        p[0] = p[1]

    def p_declaration(self, p):
        """declaration : type var"""
        p[0] = SyntaxTreeNode('declaration', value=p[1], children=p[2])

    def p_expr_list(self, p):
        """expr_list : expr_list expression
                     | expression"""
        if len(p) == 2:
            p[0] = SyntaxTreeNode('expr_list', children=p[1])
        else:
            p[0] = SyntaxTreeNode('expr_list', children=[p[1], p[2]])

    def p_type(self, p):
        """type : int
                | bool"""
        p[0] = p[1]

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

    def p_vars(self, p):
        """var : VARIABLE EQ expression
                | VARIABLE EQ L_FIGBRACKET expr_list R_FIGBRACKET"""
        if len(p) == 4:
            p[0] = SyntaxTreeNode('var', children=[p[1], p[3]])
        else:
            p[0] = SyntaxTreeNode('var', children=[p[1], p[4]])

    def p_expression(self, p):
        """expression : variable
                      | const
                      | math_expression"""
        p[1] = p[0]

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
        if len(p) == 3:
            p[0] = SyntaxTreeNode('un_op', p[2], children=p[1])
        else:
            p[0] = SyntaxTreeNode('bin_op', p[2], children=[p[1], p[3]])

    def p_const(self, p):
        """const : TRUE
                 | FALSE
                 | INT_DEC
                 | INT_BIN"""
        p[0] = SyntaxTreeNode('const', value=p[1])

    def p_variable(self, p):
        """variable : VARIABLE
                    | VARIABLE LBRACKET index RBRACKET"""
        if len(p) == 2:
            p[0] = SyntaxTreeNode('variable', p[1])
        else:
            p[0] = SyntaxTreeNode('indexing', p[1], children=p[3])

    def p_ind_exp(self, p):
        """ind_exp : expression
                   | COLON
                   | """
        p[0] = p[1]

    def p_index(self, p):
        """index : expression
                 | ind_exp COMMA ind_exp"""
        if len(p) == 2:
            p[0] = SyntaxTreeNode('index', children=p[1])
        else:
            p[0] = SyntaxTreeNode('index', children=[p[1], p[3]])

    def p_operation(self, p):
        """operation : MOVE LBRACKET math_expression RBRACKET
                     | RIGHT
                     | LEFT
                     | WALL
                     | EXIT"""
        if len(p) == 2:
            p[0] = SyntaxTreeNode('operator', p[1])
        else:
            p[0] = SyntaxTreeNode('operator', p[1], children=p[3])

    def p_assigment(self, p):
        """assigment : variable ASSIGMENT expression"""
        p[0] = SyntaxTreeNode('assigment', p[1], children=p[3])

    def p_for(self, p):
        """for : FOR VARIABLE EQ expression COLON expression BEGINFOR stmt_list ENDFOR
               | FOR VARIABLE EQ expression COLON expression BEGIN stmt_list END"""
        p[0] = SyntaxTreeNode('for', children=[p[2], p[4], p[6], p[8]])

    def p_error(self, p):
        print(f'Syntax error at {p}')
        self.acc = False


if __name__ == '__main__':
    parser = MyParser()
    txt = '1+1 \n 1-2 \n'
    print(f'INPUT: {txt}')
    tree, func_table = parser.parse(txt)
    # tree = parser.parser.parse(txt, debug=True)
    tree.print()
