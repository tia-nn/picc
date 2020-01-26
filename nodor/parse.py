from typing import List, Union, Callable, Optional, Tuple
from dataclasses import dataclass
from string import hexdigits, octdigits, digits
import re

from tokenor.tokenor import Token, TokenType, Tokenizer
from .base import BaseParser, TokenParser, saveposition, Unmatch, ParseError, unmatch_is_error
from .node import *


integer_re = re.compile(r'^(?P<prefix>0[a-zA-Z]?)?(?P<value>[0-9a-fA-F]+)(?P<suffix>[a-zA-Z]+)?$')
number_prefix_re = re.compile(r'^(?P<prefix>0[a-zA-Z]?)?')
int_value_re = re.compile(r'^(?P<value>[1-9a-fA-F][0-9a-fA-F]*)')
number_suffix_re = re.compile(r'^(?P<suffix>[a-zA-Z]+)?$')


class Nodor(BaseParser):

    def parse(self, tokens: List[Token]) -> Node:
        self.tokens = tokens
        self.p = 0
        return self.add()

    def add(self) -> Expression:
        result = self.mul()
        while True:
            if (token := self.consume('+')):
                result = Add(result, self.mul())
                continue
            break
        return result

    def mul(self) -> Expression:
        result = self.number()
        while True:
            if (token := self.consume('*')):
                result = Mul(result, self.number())
                continue
            break
        return result

    def number(self) -> Number:
        if self.token().type == TokenType.NUMBER:
            num = NumberParser().parse(self.token())
            self.p += 1
            return num
        raise Unmatch(self.p, 'not number')


class NumberParser(TokenParser):
    base: dict = {None: 10, '0x': 16, '0X': 16, '0': 8, '0o': 8, '0O': 8, '0b': 2, '0B': 2}

    def parse(self, token: Token) -> Number:
        return self.integer(token.value)

    @staticmethod
    def integer(s: str) -> Integer:
        m = integer_re.match(s)

        if m is None:
            raise Unmatch(0, 'not integer')

        v = m.groupdict()
        prefix, value, suffix = v['prefix'], v['value'], v['suffix']
        if prefix is not None:
            prefix = prefix.lower()
        if suffix is not None:
            suffix = suffix.lower()

        if prefix not in (None, '0x', '0', '0o', '0b'):
            raise ParseError(0, f'unknown integer prefix: {prefix}')
        if suffix not in (None, 'll', 'l', 'u', 'llu', 'ull', 'ul', 'lu'):
            raise ParseError(len(prefix or '') + len(value), f'unknown suffix: {suffix}')

        try:
            return Integer(int(value, base=NumberParser.base[prefix]), prefix, suffix)
        except ValueError:
            raise ParseError(len(prefix), f'there is a invalid char of base {NumberParser.base[prefix]} number')
