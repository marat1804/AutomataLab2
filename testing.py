import unittest
from interpreter import Interpreter
from interpreter import Variable
from Parser.parser import MyParser
from interpreter import create_robot


class Tests(unittest.TestCase):

    def test_bubbleSort(self):
        with open('Tests/bubblesort.txt') as f:
            text = f.read()
        f.close()
        interpreter1 = Interpreter(MyParser())
        interpreter1.interpreter(program=text)
        self.assertEqual(interpreter1.symbol_table[0]['vector'].value, [Variable('int', 9), Variable('int', 7), Variable('int', 5), Variable('int', 4), Variable('int', 2), Variable('int', 1)])
        self.assertEqual(interpreter1.symbol_table[0]['res'].value, True)

    def test_fibonacci(self):
        with open("Tests/fib.txt") as f:
            text = f.read()
        f.close()
        interpreter2 = Interpreter(MyParser())
        interpreter2.interpreter(program=text)
        self.assertEqual(interpreter2.symbol_table[0]['res'].value, 55)

    def test_indexint(self):
        with open("Tests/index.txt") as f:
            text = f.read()
        f.close()
        interpreter3 = Interpreter(MyParser())
        interpreter3.interpreter(program=text)
        self.assertEqual(interpreter3.symbol_table[0]['s'].value, 2)
        self.assertEqual(interpreter3.symbol_table[0]['s1'].value, 1)
        self.assertEqual(interpreter3.symbol_table[0]['v1'].value, [Variable('int', 2), Variable('int', 5), Variable('int', 8)])
        self.assertEqual(interpreter3.symbol_table[0]['v2'].value, [Variable('int', 4), Variable('int', 5), Variable('int', 6)])
        self.assertEqual(interpreter3.symbol_table[0]['v3'].value, [Variable('int', 1), Variable('int', 3)])
        self.assertEqual(interpreter3.symbol_table[0]['m1'].value, [[Variable('int', 1), Variable('int', 4), Variable('int', 7)], [Variable('int', 3), Variable('int', 6), Variable('int', 9)]])
        self.assertEqual(interpreter3.symbol_table[0]['m2'].value, [[Variable('int', 1), Variable('int', 2), Variable('int', 3)], [Variable('int', 7), Variable('int', 8), Variable('int', 9)]])
        self.assertEqual(interpreter3.symbol_table[0]['m3'].value, [[Variable('int', 1), Variable('int', 4), Variable('int', 7)], [Variable('int', 3), Variable('int', 6), Variable('int', 9)]])
        self.assertEqual(interpreter3.symbol_table[0]['m4'].value, [[Variable('int', 1), Variable('int', 2), Variable('int', 3)], [Variable('int', 7), Variable('int', 8), Variable('int', 9)]])
        self.assertEqual(interpreter3.symbol_table[0]['m6'].value, [[Variable('int', 1), Variable('int', 2)], [Variable('int', 4), Variable('int', 6)], [Variable('int', 8), Variable('int', 9)]])

    def test_math(self):
        with open("Tests/math.txt") as f:
            text = f.read()
        f.close()
        interpreter3 = Interpreter(MyParser())
        interpreter3.interpreter(program=text)
        self.assertEqual(interpreter3.symbol_table[0]['res1'].value, 5)
        self.assertEqual(interpreter3.symbol_table[0]['res2'].value, 7)
        self.assertEqual(interpreter3.symbol_table[0]['res3'].value, -1)
        self.assertEqual(interpreter3.symbol_table[0]['matmul_1'].value, [[Variable('int', 22), Variable('int', 28)], [Variable('int', 49), Variable('int', 64)]])
        self.assertEqual(interpreter3.symbol_table[0]['matres2'].value, [[Variable('int', 9), Variable('int', 12), Variable('int', 15)], [Variable('int', 19), Variable('int', 26), Variable('int', 33)], [Variable('int', 29), Variable('int', 40), Variable('int', 51)]])
        self.assertEqual(interpreter3.symbol_table[0]['matmul_3'].value, [[Variable('int', 3), Variable('int', 6)], [Variable('int', 9), Variable('int', 12)]])
        self.assertEqual(interpreter3.symbol_table[0]['elemmul_2'].value, [[Variable('int', 1), Variable('int', 4)], [Variable('int', 9), Variable('int', 16)]])
        self.assertEqual(interpreter3.symbol_table[0]['transpose'].value, [[Variable('int', 1), Variable('int', 3)], [Variable('int', 2), Variable('int', 4)]])
        self.assertEqual(interpreter3.symbol_table[0]['elemsum'].value, 10)
        self.assertEqual(interpreter3.symbol_table[0]['n2'].value, 5)
        self.assertEqual(interpreter3.symbol_table[0]['n3'].value, 3)
        self.assertEqual(interpreter3.symbol_table[0]['var_1'].value, True)
        self.assertEqual(interpreter3.symbol_table[0]['var_2'].value, True)
        self.assertEqual(interpreter3.symbol_table[0]['var_3'].value, True)
        self.assertEqual(interpreter3.symbol_table[0]['var_4'].value, False)
        self.assertEqual(interpreter3.symbol_table[0]['var_5'].value, False)
        self.assertEqual(interpreter3.symbol_table[0]['var_6'].value, True)
        self.assertEqual(interpreter3.symbol_table[0]['var_7'].value, True)


if __name__ == '__main__':
    unittest.main()
