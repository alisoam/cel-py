# mypy: disable-error-code="has-type"
# pylint: disable=invalid-name

from pathlib import Path
from typing import Self

from lark import Lark, Transformer
from lark.lexer import Token
from lark.tree import Meta

CEL_GRAMER = (Path(__file__).parent / "cel.lark").read_text()
CEL_PARSER = Lark(CEL_GRAMER, start="expr")

DUMMY_RULES = {"member", "primary", "literal", "ident"}
SPECIAL_MACROS = {"filter", "map", "exists", "exists_once", "all"}
BLACK_LIST = {
    "open",
    "import",
    "for",
    "while",
    "break",
    "continue",
    "if",
    "else",
    "elif",
    "def",
    "class",
    "super",
    "aiter",
    "iter",
    "anext",
    "next",
    "dir",
    "vars",
    "globals",
    "locals",
    "id",
    "compile",
    "exec",
    "eval",
    "setattr",
    "getattr",
    "hasattr",
    "delattr",
    "input",
    "print",
    "memoryview",
    "help",
}


class CELError(Exception):
    pass


class Parser(Transformer):  # pylint: disable=too-many-public-methods
    def __default__(self: Self, data: Token, children: list[str], meta: Meta) -> str:
        assert data in DUMMY_RULES
        assert len(children) == 1
        return children[0]

    def IDENT(self: Self, data: Token) -> str:
        if data.value in BLACK_LIST or (data.value.startswith("__") and data.value.endswith("__")):
            raise CELError(f"identity {data.value} not allowed")

        return data.value

    def INT_LIT(self: Self, data: Token) -> str:
        return data.value

    def FLOAT_LIT(self: Self, data: Token) -> str:
        return data.value

    def MLSTRING_LIT(self: Self, data: Token) -> str:
        return data.value

    def STRING_LIT(self: Self, data: Token) -> str:
        return data.value

    def BOOL_LIT(self: Self, data: Token) -> str:
        return "True" if data == "true" else "False"

    def NULL_LIT(self: Self, _) -> str:
        return "None"

    def expr(self: Self, data: list[Token]) -> str:
        match data:
            case [expr, None, None]:
                return expr
            case [cond, left, right]:
                return f"({left}) if {cond} else ({right})"
            case _:
                raise CELError(f"expr data: {data} mismatch")

    def conditionalor(self: Self, data: list[Token]) -> str:
        match data:
            case [None, value]:
                return value
            case [left, right]:
                return f"({left}) or ({right})"
            case _:
                raise CELError(f"conditionalor data: {data} mismatch")

    def conditionaland(self: Self, data: list[Token]) -> str:
        match data:
            case [None, value]:
                return value
            case [left, right]:
                return f"({left}) and ({right})"
            case _:
                raise CELError(f"condionaland data: {data} mismatch")

    def relation(self: Self, data: list[Token]) -> str:
        match data:
            case [None, value]:
                return value
            case [(left, op), right]:
                return f"({left}) {op} ({right})"
            case _:
                raise CELError(f"relation data: {data} mismatch")

    def relation_lt(self: Self, data: list[Token]) -> list[str]:
        (value,) = data
        return [value, "<"]

    def relation_le(self: Self, data: list[Token]) -> list[str]:
        (value,) = data
        return [value, "<="]

    def relation_gt(self: Self, data: list[Token]) -> list[str]:
        (value,) = data
        return [value, ">"]

    def relation_ge(self: Self, data: list[Token]) -> list[str]:
        (value,) = data
        return [value, ">="]

    def relation_eq(self: Self, data: list[Token]) -> list[str]:
        (value,) = data
        return [value, "=="]

    def relation_ne(self: Self, data: list[Token]) -> list[str]:
        (value,) = data
        return [value, "!="]

    def relation_in(self: Self, data: list[Token]) -> list[str]:
        (value,) = data
        return [value, "in"]

    def addition(self: Self, data: list[Token]) -> str:
        match data:
            case [None, value]:
                return value
            case [(left, op), right]:
                return f"({left}) {op} ({right})"
            case _:
                raise CELError(f"addition data: {data} mismatch")

    def addition_sub(self: Self, data: list[Token]) -> list[str]:
        (value,) = data
        return [value, "-"]

    def addition_add(self: Self, data: list[Token]) -> list[str]:
        (value,) = data
        return [value, "+"]

    def multiplication(self: Self, data: list[Token]) -> str:
        match data:
            case [None, value]:
                return value
            case [(left, op), right]:
                return f"({left}) {op} ({right})"
            case _:
                raise CELError(f"multiplication data: {data} mismatch")

    def multiplication_mul(self: Self, data: list[Token]) -> list[str]:
        (value,) = data
        return [value, "*"]

    def multiplication_div(self: Self, data: list[Token]) -> list[str]:
        (value,) = data
        return [value, "/"]

    def multiplication_mod(self: Self, data: list[Token]) -> list[str]:
        (value,) = data
        return [value, "%"]

    def unary(self: Self, data: list[Token]) -> str:
        match data:
            case [value]:
                return value
            case [op, value]:
                return f"({op} {value})"
            case _:
                raise CELError(f"unary data: {data} mismatch")

    def unary_not(self: Self, _: list) -> str:
        return "not"

    def unary_neg(self: Self, _) -> str:
        return "-"

    def paren_expr(self: Self, data: list[Token]) -> str:
        (value,) = data
        return "(" + value + ")"

    def list_lit(self: Self, data: list[Token]) -> str:
        (value,) = data
        return "[" + value + "]"

    def exprlist(self: Self, data: list[Token]) -> str:
        return ",".join(data)

    def map_lit(self: Self, data: list[Token]) -> str:
        (value,) = data
        return "{" + value + "}"

    def mapinits(self: Self, data: list[Token]) -> str:
        return ",".join(data)

    def mappair(self: Self, data: list[Token]) -> str:
        key, value = data
        return key + ": " + value

    def member_dot(self: Self, data: list[Token]) -> str:
        member, ident = data
        return f'{member}.get("{ident}", None) if isinstance({member}, dict) else getattr({member}, "{ident}", None)'

    def member_dot_arg(self: Self, data: list[Token]) -> str:
        member, function, exprlist = data
        if function in SPECIAL_MACROS:
            assert "," in exprlist
            # convert iterator.filter(x, x > 0) to filter(lambda x: x > 0, iterator)
            func = "lambda " + exprlist.replace(",", ":", 1)
            macro = "None"
            match function:
                case "filter":
                    macro = "(lambda func, it: list(filter(func, it)))"
                case "map":
                    macro = "(lambda func, it: list(map(func, it)))"
                case "all":
                    macro = "(lambda func, it: all(map(func, it)))"
                case "exists":
                    macro = "(lambda func, it: any(map(func, it)))"
                case "exists_once":
                    macro = "(lambda func, it: sum(map(lambda x: 1 if func(x) else 0, it)) == 1)"

            return f"{macro}({func}, {member})"

        if function == "has":
            raise CELError("has not allowed for members")

        return f"{member}.{function}(exprlist)"

    def member_index(self: Self, data) -> str:
        member, index = data
        return f"{member}[{index}]"

    def ident_arg(self: Self, data: list[Token]) -> str:
        ident, arg = data
        assert ident not in ["filter", "all", "exists", "exists_once"]
        if ident == "has":
            return f"({arg}) is not None "

        return f"{ident}({arg})"


class Program:
    def __init__(self: Self, code) -> None:
        self.code = code

    def eval(self: Self, args: dict | None = None) -> dict[str, int] | (bool | (list[int] | float)):
        local_variables = args or {}
        exec(self.code, {}, local_variables)  # pylint: disable=exec-used
        return local_variables["___exec_return"]


class Compiler:
    PARSER = Parser()

    @classmethod
    def compile(cls: type[Self], text: str) -> Program:
        try:
            ast = CEL_PARSER.parse(text)
            code = compile(f"___exec_return = ({cls.PARSER.transform(ast)})", "", "exec")
            return Program(code)
        except Exception as exc:
            raise CELError from exc
