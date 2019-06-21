from typing import List, Union
from dataclasses import dataclass
from enum import Enum, auto

from type import Type
from tokenizer import TK, Token


class ParseError(Exception):
    pass


class ND(Enum):
    constant = auto()


@dataclass
class Node:
    ty: ND
    type: Type
    val: Union[int, str]


class ParseUtils:
    p: int
    tokens: List[Token]

    def pos(self):
        ret = self.tokens[self.p]
        self.p += 1
        return ret

    def next_is(self, ty):
        return self.tokens[self.p].ty == ty

    def next_in(self, tys):
        return self.tokens[self.p].ty in tys

    def consume(self, ty):
        if self.next_is(ty):
            self.p += 1
            return True
        return False

    def consume_must(self, ty):
        if self.next_is(ty):
            return self.pos()
        raise ParseError(f'at consume_must({ty})')

    @staticmethod
    def caller(*methods):
        for method in methods:
            try:
                return method()
            except ParseError:
                pass
        raise ParseError

    def token_consumer(self, tokens):
        if self.next_in(tokens):
            return self.pos().ty
        raise ParseError

    @staticmethod
    def repeat(method, allow_null=True):
        ret = []
        while True:
            try:
                ret.append(method())
            except ParseError:
                break
        if not allow_null and not ret:
            raise ParseError
        return ret

    @staticmethod
    def select(method):
        try:
            return method()
        except ParseError:
            return None


class Parser(ParseUtils):
    p: int
    tokens: List[Token]

    def parse(self, tokens):
        self.p = 0
        nodes = []
        self.tokens = tokens
        while not self.consume(TK.EOF):
            nodes.append(self.constant())
        return nodes

    def constant(self):
        if self.next_is(TK.NUM):
            t = self.pos()
            return Node(ND.constant, type=t.type, val=t.val)


if __name__ == '__main__':
    from sys import argv
    from tokenizer import Tokenizer

    argc = len(argv)

    if argc > 1:
        if argv[1] == 'test':
            t = Tokenizer()
            tokens = t.tokenize('0xff')
            p = Parser()
            nodes = p.parse(tokens)
            print(nodes)
