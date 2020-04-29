import sys
from typing import List
from parser import MyParser, SyntaxTreeNode


class Variable:
    def __init__(self, var_type, var_value):
        self.type = var_type
        if var_value == 'true':
            self.value = True
        elif var_value == 'false':
            self.value = False
        else:
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
            return Variable('int', 0)


class Interpreter:

    def __init__(self, parser, converser):
        self.parser = parser
        self.converser = converser
        self.map = None
        self.program = None
        self.symbol_table = dict()
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
            return self.const_val(node.value)
        elif node.type == 'decl_list':
            return self.list_of_smth(self.get_list(node))
        elif node.type == 'variable':
            return self.get_value(node)
        elif node.type == 'assigment':
            var = node.value.value
            if var not in self.symbol_table.keys():
                print('ERROR')  # TODO Error
            else:
                _type = self.symbol_table[var].type
                expression = self.interpreter_node(node.children)
                # TODO add Try
                self.assign(_type, var, expression)
        elif node.type == 'bin_op':
            if node.value == '+':
                return self.bin_plus(node.children[0], node.children[1])
            elif node.value == '-':
                return self.bin_minus(node.children[0], node.children[1])
            elif node.value == '*':
                return self.matrix_mul(node.children[0], node.children[1])
        else:
            print('ELSE', node)
        return ''

    def get_value(self, node):
        if node.value in self.symbol_table.keys():
            return self.symbol_table[node.value]
        else:
            print("ERRROR")

    def declare_variable(self, type, child):
        if child[1].type == 'decl_list':
            variable = child[0].value
            expression = self.interpreter_node(child[1])
            self.declare(type, variable, expression)
        elif child[1].type == 'expression':
            variable = child[0].value
            expression = self.interpreter_node(child[1])
            # TODO try
            self.declare(type, variable, expression)

    def declare(self, type, var, expression):
        expression = self.check_type(type, expression)
        if var in self.symbol_table.keys():
            pass  # TODO ERROR
        else:

            self.symbol_table[var] = expression

    def get_list(self, node):
        if isinstance(node.children, SyntaxTreeNode):
            expression = self.interpreter_node(node.children)
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

    def check_type(self, type, exp):
        if type.find('m') != -1:
            e = self.check_matrix(type, exp)
        elif type.find('v') != -1:
            e = self.check_vector(type, exp)
        else:
            e = self.check_var(type, exp)
        return e

    def check_matrix(self, type, expr):
        exp = expr.value
        l = len(exp)
        t = type[1:]
        for i in range(len(exp)):
            if len(exp[i]) != l:
                print('ERROR')
                # TODO Error
        for i in range(l):
            for j in range(l):
                exp[i][j] = self.converser.converse(t, exp[i][j])
        return Variable(type, exp)

    def check_vector(self, type, expr):
        t = type[1:]
        exp = expr.value
        for i in range(len(exp)):
            exp[i] = self.converser.converse(t, exp[i])
        return Variable(type, exp)

    def check_var(self, type, exp):
        exp = self.converser.converse(type, exp)
        return exp

    def const_val(self, value):
        if value == 'true' or value == 'false':
            return Variable('bool', value)
        else:
            return Variable('int', value)

    def list_of_smth(self, value):
        if isinstance(value[0], list):
            if isinstance(value[0][0].value, int):
                return Variable('mint', value)
            else:
                return Variable('mbool', value)
        else:
            if isinstance(value[0].value, int):
                return Variable('vint', value)
            else:
                return Variable('vbool', value)

    def assign(self, type, var, expression):
        if type[0] == 'c':
            print("ERRROR")  # TODO ERROR
        if type == expression.type:
            self.symbol_table[var] = expression
        elif type[0] == expression.type[0]:
            if type[0] == 'v':
                self.symbol_table[var] = self.check_vector(type, expression)
            elif type[0] == 'm':
                self.symbol_table[var] = self.check_matrix(type, expression)
        elif (type == 'bool' or type == 'int') and (expression.type == 'bool' or expression.type == 'int'):
            self.symbol_table[var] = self.check_var(type, expression)
        else:
            print('ERRORR')  # TODO EROOR

    def bin_plus(self, var1, var2):
        expr1 = self.converser.converse('int', self.interpreter_node(var1))
        expr2 = self.converser.converse('int', self.interpreter_node(var2))
        return Variable('int', expr1.value + expr2.value)

    def bin_minus(self, var1, var2):
        expr1 = self.converser.converse('int', self.interpreter_node(var1))
        expr2 = self.converser.converse('int', self.interpreter_node(var2))
        return Variable('int', expr1.value - expr2.value)

    def matrix_mul(self, var1, var2):
        expr1 = self.interpreter_node(var1)
        expr2 = self.interpreter_node(var2)
        if expr1.type.find('m') == -1:
            print('not_matrix')  # TODO add EROOOR
        else:
            expr1 = self.check_matrix('mint', expr1)
        if expr2.type.find('m') == -1:
            expr2 = self.converse_to_matrix(expr2, len(expr1.value))
        else:
            expr2 = self.check_matrix('mint', self.interpreter_node(var2))
        res = []
        l = len(expr1.value)
        for i in range(l):
            res.append([Variable('int', 0) for j in range(l)])
        for i in range(l):
            for j in range(l):
                for k in range(l):
                    res[i][j].value += expr1.value[i][k].value * expr2.value[k][j].value
        return Variable('mint', res)

    def converse_to_matrix(self, value, size):
        m = []
        for i in range(size):
            m.append([Variable('int', 0) for j in range(size)])
        val = self.converser.converse('int', value)
        for i in range(size):
            m[i][i] = val
        return m


if __name__ == '__main__':
    i = Interpreter(MyParser, TypeConverser())
    prog = open('test1.txt', 'r').read()
    m = MyParser()
    tree, f = m.parse(prog)
    i.interpreter_node(tree)
    for k,v in i.symbol_table.items():
        print(k, v)
