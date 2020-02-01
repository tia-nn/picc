from typing import List, Callable, Union, Sequence, Any, Generic, TypeVar, Optional

from tokenor import Token, TokenType
from ..node import Node


T = TypeVar('T')


class Unmatch(Exception):
    position: int

    def __init__(self, position: int, info: str):
        super().__init__(info)
        self.position = position


class ParseError(Exception):
    position: int

    def __init__(self, position: int, info: str):
        super().__init__(info)
        self.position = position


def unmatch_is_error(fn: Callable[[], T], info: Optional[str] = None) -> T:
    try:
        return fn()
    except Unmatch as e:
        raise ParseError(e.position, *([info] if info is not None else e.args))


class Base:
    p: int

    def select(self, *funcs: Callable[[], Node]) -> Node:
        for i in range(len(funcs)):
            try:
                return funcs[i]()
            except Unmatch as e:
                continue
        raise Unmatch(self.p, 'select unmatched')


class BaseParser(Base):
    tokens: List[Token]

    def token(self) -> Token:
        try:
            return self.tokens[self.p]
        except IndexError:
            raise Unmatch(self.p, 'token index out of range')

    def consume(self, token_type: Union[TokenType, str]) -> Optional[Token]:
        try:
            token = self.token()
        except Unmatch:
            return None
        if token.type == token_type:
            self.p += 1
            return token
        return None

    def binary_expression(self, fn: Callable[[], Node], token_type: str, nd: Callable[[int, Node, Node], Node]) -> Node:
        result = fn()
        while (token := self.consume(token_type)):
            result = nd(self.p-1, result, unmatch_is_error(fn, 'no left operand'))
        return result


class TokenParser(Base):
    code: str
    p: int

