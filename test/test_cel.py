from typing import Self
from unittest.mock import Mock

from django.test import TestCase

from bidmeshk import cel


class TestDataclass(TestCase):
    def test_expression(self: Self) -> None:
        text = """ false ? -100 : (1 + 2) * 105 - -3 + (10/2) - 1.5 """

        program = cel.Compiler.compile(text)
        result = program.eval()

        self.assertEqual(result, 321.5)

    def test_condition(self: Self) -> None:
        text = """ true && (false || true) """

        program = cel.Compiler.compile(text)
        result = program.eval()

        self.assertEqual(result, True)

    def test_relation(self: Self) -> None:
        text = """
            (1 < 2) && (1 <= 2) && ( 2 > 1) && (2 >= 1) && (1 == 1) && (1 != 2)
            && (1 in [1, 2, 3]) && !(1 in [2, 3])  && (1 in {1: 11, 2: 12 , 3: 13}) && !(1 in {2: 12, 3: 13})
        """

        program = cel.Compiler.compile(text)
        result = program.eval()

        self.assertEqual(result, True)

    def test_list(self: Self) -> None:
        text = """[1, 2, 3]"""

        program = cel.Compiler.compile(text)
        result = program.eval()

        self.assertEqual(result, [1, 2, 3])

    def test_dict(self: Self) -> None:
        text = """ {"a": 1, "b": 2, "c": 3} """

        program = cel.Compiler.compile(text)
        result = program.eval()

        self.assertEqual(result, {"a": 1, "b": 2, "c": 3})

    def test_member_dot(self: Self) -> None:
        text = """ dct.a == 1"""
        tests = [
            ({"a": 1, "b": 2, "c": 3},),
            (Mock(a=1, b=2, c=3),),
        ]

        program = cel.Compiler.compile(text)
        for (dct,) in tests:
            _ = dct
            result = program.eval({"dct": dct})

            self.assertTrue(result)

    def test_member_macros(self: Self) -> None:
        tests = [
            (""" [1, 2, 3, 4].filter(x, x >= 3)""", [3, 4]),
            (""" [1, 2, 3, 4].exists(x, x >= 3)""", True),
            (""" [1, 2, 3, 4].exists(x, x >= 5)""", False),
            (""" [1, 2, 3, 4].exists_once(x, x >= 3)""", False),
            (""" [1, 2, 3, 4].exists_once(x, x >= 4)""", True),
            (""" [1, 2, 3].all(x, x > 1)""", False),
            (""" [1, 2, 3].all(x, x >= 1)""", True),
            (""" [1, 2, 3].all(x, x >= 1)""", True),
            (""" [1, 2, 3].map(x, x * (10 * x + 1))""", [11, 42, 93]),
        ]
        for text, result in tests:
            program = cel.Compiler.compile(text)
            test_result = program.eval()

            self.assertEqual(result, test_result)

    def test_has_macros(self: Self) -> None:
        class ClsA:
            a = 12

        class ClsB:
            b = 12

        dcta = {"a": 12, "b": 12}
        dctb = {"b": 12}
        args = {
            "ClsA": ClsA,
            "ClsB": ClsB,
            "dcta": dcta,
            "dctb": dctb,
        }
        tests = [
            (""" has(dcta.a) """, True),
            (""" has(dctb.a) """, False),
            (""" has(ClsA.a) """, True),
            (""" has(ClsB.a) """, False),
        ]
        for text, result in tests:
            program = cel.Compiler.compile(text)
            test_result = program.eval(args)

            self.assertEqual(result, test_result)

    def test_blacklists(self: Self) -> None:
        tests = [
            "import x",
            "__import__(x)",
        ]
        for text in tests:
            with self.assertRaises(cel.CELError):
                cel.Compiler.compile(text)
