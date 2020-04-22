from lexerClass import MyLexer
import ply.yacc as yacc
from typing import List, Optional


class SyntaxTreeNode:
    def __init__(self, node_type, value = None, children: Optional[List[SyntaxTreeNode]] = None):
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
