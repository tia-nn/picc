from typing import List, Callable, Union, Sequence

from tokenor.tokenor import Token
from .node import Node


class Unmatch(Exception):
    position: int

    def __init__(self, position, info):
        super().__init__(info)
        self.position = position


class ParseError(Exception):
    position: int

    def __init__(self, position, info):
        super().__init__(info)
        self.position = position


class Base:
    p: int

    def select(self, funcs: Sequence[Callable]):
        for i in range(len(funcs)):
            try:
                return funcs[i]()
            except Unmatch as e:
                continue
        raise Unmatch(self.p, 'select unmatched')


class BaseParser(Base):
    tokens: List[Token]

    def token(self) -> Token:
        return self.tokens[self.p]


class TokenParser(Base):
    code: str
    p: int


def saveposition(f: Callable[[Union[BaseParser, TokenParser]], Node]):
    def wrap(self: Union[BaseParser, TokenParser], *args, **kwargs):
        try:
            p = self.p
            ret = f(self)
        except Unmatch as e:
            self.p = p
            raise e
        return ret
    return wrap

