from typing import List, Callable, Union, Sequence, Any, Generic, TypeVar

from tokenor.tokenor import Token
from .node import Node


T = TypeVar('T')


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


def unmatch_is_error(fn: Callable[[], T]) -> T:
    try:
        return fn()
    except Unmatch as e:
        raise ParseError(e.position, *e.args)


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

    def consume(self, token_type) -> Union[Token, bool]:
        try:
            token = self.token()
        except IndexError:
            return False
        if token == token_type:
            self.p += 1
            return token
        return False


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

