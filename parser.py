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
        p[0] = SyntaxTreeNode('program', children=p[1])

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
        """statement : al_expression NL"""
        p[0] = SyntaxTreeNode('stmt_list', value=p[1])

    def p_al_expression(self, p):
        """al_expression : INT_DEC PLUS INT_DEC
        | INT_DEC MINUS INT_DEC"""
        p[0] = SyntaxTreeNode('op', p[2], children=[p[1], p[3]])

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
