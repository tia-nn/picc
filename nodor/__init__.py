from typing import List, Union, Callable, Optional, Tuple
from dataclasses import dataclass
from string import hexdigits, octdigits, digits
import re

from tokenor import Token, TokenType, Tokenizer
from .base import BaseParser, TokenParser, saveposition, Unmatch, ParseError, unmatch_is_error
from .node import *

integer_re = re.compile(r'^(?P<prefix>0[a-zA-Z]?)?(?P<value>[0-9a-fA-F]+)(?P<suffix>[a-zA-Z]+)?$')
number_prefix_re = re.compile(r'^(?P<prefix>0[a-zA-Z]?)?')
int_value_re = re.compile(r'^(?P<value>[1-9a-fA-F][0-9a-fA-F]*)')
number_suffix_re = re.compile(r'^(?P<suffix>[a-zA-Z]+)?$')


class Nodor(BaseParser):

    def parse(self, tokens: List[Token]) -> List[Node]:
        self.tokens = tokens
        self.p = 0
        nodes = []
        while not self.consume(TokenType.EOF):
            nodes.append(self.expression_statement())
        return nodes

    def expression_statement(self) -> Statement:
        result = self.expression()
        if not self.consume(';'):
            raise ParseError(self.p, 'expression statement: no ";"')
        return result

    def expression(self):
        return self.assign()

    def assign(self) -> Expression:
        result = self.add()
        while True:
            if (token := self.consume('=')):
                result = Assign(self.p, result, unmatch_is_error(self.assign, 'no left operand'))
                continue
            break
        return result

    def add(self) -> Expression:
        return self.binary_expression(self.mul, '+', Add)

    def mul(self) -> Expression:
        return self.binary_expression(self.primary_expression, '*', Mul)

    def primary_expression(self) -> PrimaryExpression:
        return self.select(self.number, self.variable, self.bracket)

    def bracket(self) -> Expression:
        if self.consume('('):
            result = self.expression()
            if not self.consume(')'):
                raise ParseError(self.p, 'no ")"')
            return result
        raise Unmatch(self.p, 'no "("')

    def number(self) -> Number:
        if self.token().type == TokenType.NUMBER:
            num = NumberParser().parse(self.token(), self.p)
            self.p += 1
            return num
        raise Unmatch(self.p, 'not number')

    def variable(self) -> Variable:
        from string import ascii_lowercase
        for i in ascii_lowercase:
            if self.consume(i):
                return Variable(self.p, i)
        raise Unmatch(self.p, 'not variable')


class NumberParser(TokenParser):
    base: dict = {None: 10, '0x': 16, '0X': 16, '0': 8, '0o': 8, '0O': 8, '0b': 2, '0B': 2}

    def parse(self, token: Token, position: int) -> Number:
        return self.integer(token.value, position)

    @staticmethod
    def integer(s: str, position: int) -> Integer:
        m = integer_re.match(s)

        if m is None:
            raise Unmatch(position, 'not integer')

        v = m.groupdict()
        prefix, value, suffix = v['prefix'], v['value'], v['suffix']
        if prefix is not None:
            prefix = prefix.lower()
        if suffix is not None:
            suffix = suffix.lower()

        if prefix not in (None, '0x', '0', '0o', '0b'):
            raise ParseError(position, f'unknown integer prefix: {prefix}')
        if suffix not in (None, 'll', 'l', 'u', 'llu', 'ull', 'ul', 'lu'):
            raise ParseError(position + len(prefix or '') + len(value), f'unknown suffix: {suffix}')

        try:
            return Integer(position, int(value, base=NumberParser.base[prefix]), prefix, suffix)
        except ValueError:
            raise ParseError(position + len(prefix),
                             f'there is a invalid char of base {NumberParser.base[prefix]} number')
