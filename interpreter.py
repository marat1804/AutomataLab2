import sys
from typing import List
from parser import MyParser, SyntaxTreeNode


class Variable:
    def __init__(self, var_type, var_value):
        self.type = var_type
        self.value = var_value

    def __repr__(self):
        return f'{self.type} {self.value}'


class TypeConverser:
    def __init__(self):
        pass

    def converse(self, type, var):
        if type == var.type:
            return var
        elif type == 'bool':
            if var.type == 'int':
                return self.int_to_bool(var)
        elif type == 'int':
            if var.type == 'bool':
                return self.bool_to_int(var)

    @staticmethod
    def int_to_bool(var):
        if var.value == 0:
            return Variable('bool', False)
        else:
            return Variable('bool', True)

    @staticmethod
    def bool_to_int(var):
        if var.value:
            return Variable('int', 1)
        else:
            return Variable('bool', 0)


class Interpreter:

    def __init__(self, parser, converser):
        self.parser = parser
        self.converser = converser
        self.map = None
        self.program = None
        self.symbol_table = [dict()]
        self.tree = None
        self.functions = None
        # TODO add errors
        self.errors = {}

    def interpreter(self, map, program):
        self.map = map
        self.program = program
        self.symbol_table = dict()
        try:
            self.tree, self.functions = self.parser.parse(program)
        # TODO Exception
        except Exception:
            pass
        self.interpreter_tree(self.tree)
        self.interpreter_node(self.functions['application'])

    def interpreter_tree(self, tree):
        pass

    def interpreter_node(self, node):
        if node is None:
            return ''
        elif node.type == 'program':
            self.interpreter_node(node.children)
        elif node.type == 'stmt_list':
            for ch in node.children:
                self.interpreter_node(ch)

        # statements
        elif node.type == 'declaration':
            declaration_type = node.value.value
            declaration_child = node.children
            self.declare_variable(declaration_type, declaration_child)
        elif node.type == 'expr_list':
            L = []
            for ch in node.children:
                L.append(self.interpreter_node(ch))
            if len(L) == 2:
                L[0].append(L[1])
                del L[1]
                L = L[0]
            return L
        elif node.type == 'expression':
            return self.interpreter_node(node.children)
        elif node.type == 'const':
            return node.value
        else:
            print('ELSE', node)
        return ''

    def declare_variable(self, type, child):
        if child[1].type == 'decl_list':
            variable = child[0]
            expression = self.get_list(child[1])
            print(type, variable, expression)
            self.declare(type, variable, expression)
        elif child[1].type == 'expression':
            variable = child[0].value
            expression = self.interpreter_node(child[1])
            # TODO try
            self.declare(type, variable, expression)

    def declare(self, type, var, expression):

        pass

    def get_list(self, node):
        if isinstance(node.children, SyntaxTreeNode):
            expression = self.interpreter_node(node.children)
            #print(node, expression)
            return expression
        elif isinstance(node.children, list):
            expr = []
            for i in node.children:
                a = self.get_list(i)
                expr.append(a)
            if len(expr) == 2:
                if len(expr[0]) != len(expr[1]):
                    expr[0].append(expr[1])
                    del expr[1]
                    expr = expr[0]
            return expr


if __name__ == '__main__':
    i = Interpreter(MyParser, '')
    prog = open('test1.txt', 'r').read()
    m = MyParser()
    tree, f = m.parse(prog)
    i.interpreter_node(tree)
