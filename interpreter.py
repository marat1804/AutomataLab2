import sys
from typing import List
from parser import MyParser


class Interpreter:

    # TODO add converser
    # TODO add errors
    def __init__(self, parser, converser):
        self.parser = parser
        self.converser = converser
        self.map = None
        self.program = None
        self.symbol_table = None
        self.tree = None
        self.functions = None
        self.errors = {}

    # TODO Exceprion
    def interpreter(self, map, program):
        self.map = map
        self.program = program
        self.symbol_table = dict()
        try:
            self.tree, self.functions = self.parser.parse(program)
        except Exception:
            pass
        self.interpreter_tree(self.tree)
        self.interpreter_node(self.functions['application'])

    def interpreter_tree(self, tree):
        pass

    def interpreter_node(self, node):
        if node is None:
            return
        elif node.type == 'program':
            self.interpreter_node(node.children)
        elif node.type == 'stmt_list':
            for ch in node.children:
                self.interpreter_node(ch)

        # statements
        elif node.type == 'declaration':
            declaration_type = node.value.value
            declaration_child = node.children
            print(declaration_type, declaration_child)


if __name__ == '__main__':
    i = Interpreter(MyParser, '')
    prog = open('test1.txt', 'r').read()
    m = MyParser()
    tree, f = m.parse(prog)
    i.interpreter_node(tree)


