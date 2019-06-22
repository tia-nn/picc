from typing import List, Union
from dataclasses import dataclass
from enum import Enum, auto

from type import Type
from tokenizer import TK, Token


class ParseError(Exception):
    pass


class ND(Enum):
    INT = auto()


@dataclass
class Node:
    ty: Union[ND, str]
    type: Type
    val: Union[int, str] = None
    lhs: 'Node' = None
    rhs: 'Node' = None


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
        return ParseError

    @staticmethod
    def caller(*methods):
        for method in methods:
            if (ret := method()) != ParseError:
                return ret
        return ParseError

    def token_consumer(self, tokens):
        if self.next_in(tokens):
            return self.pos().ty
        return ParseError

    @staticmethod
    def repeat(method, allow_null=True):
        ret = []
        while True:
            if (m := method()) != ParseError:
                ret.append(method())
            else:
                continue
        if not allow_null and not ret:
            return ParseError
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

    # lexical-element

    def constant(self):
        if self.next_is(TK.NUM):
            t = self.pos()
            return Node(ND.INT, type=t.type, val=t.val)
        return ParseError

    # expression

    def primary_expression(self):
        if (c := self.constant()) != ParseError:
            return c
        if self.consume('('):
            expression = self.expression()
            self.consume_must(')')
            return expression
        return ParseError

    def postfix_expression(self):
        postfix = self.primary_expression()

        while True:
            break

        return postfix

    def unary_expression(self):
        unary = self.postfix_expression()

        while True:
            if self.consume('+'):
                pass
            if self.consume('-'):
                unary = Node('*', type=unary.type, lhs=unary, rhs=Node(ND.INT, type=Type('int', signed=True), val=-1))
            if self.consume('!'):
                unary = Node('!', type=unary.type, lhs=unary)
            break

        return unary

    def cast_expression(self):
        cast = self.unary_expression()

        while True:
            break

        return cast

    def multiple_expression(self):
        mul = self.cast_expression()

        while True:
            if self.consume('*'):
                mul = Node('*', type=mul.type, lhs=mul, rhs=self.cast_expression())
                continue
            if self.consume('/'):
                mul = Node('/', type=mul.type, lhs=mul, rhs=self.cast_expression())
                continue
            if self.consume('%'):
                mul = Node('%', type=mul.type, lhs=mul, rhs=self.cast_expression())
                continue
            break

        return mul

    def additive_expression(self):
        add = self.multiple_expression()

        while True:
            if self.consume('+'):
                add = Node('+', type=add.type, lhs=add, rhs=self.multiple_expression())
                continue
            if self.consume('-'):
                add = Node('-', type=add.type, lhs=add, rhs=self.multiple_expression())
                continue
            break

        return add

    def shift_expression(self):
        shift = self.additive_expression()

        while True:
            if self.consume('>>'):
                shift = Node('>>', type=shift.type, lhs=shift, rhs=self.additive_expression())
                continue
            if self.consume('<<'):
                shift = Node('<<', type=shift.type, lhs=shift, rhs=self.additive_expression())
                continue
            break

        return shift

    def relational_expression(self):
        relational = self.shift_expression()

        while True:
            if self.consume('<'):
                relational = Node('<', type=relational.type, lhs=relational, rhs=self.shift_expression())
                continue
            if self.consume('>'):
                relational = Node('<', type=relational.type, rhs=relational, lhs=self.shift_expression())
                continue
            if self.consume('<='):
                relational = Node('<=', type=relational.type, lhs=relational, rhs=self.shift_expression())
                continue
            if self.consume('>='):
                relational = Node('<=', type=relational.type, rhs=relational, lhs=self.shift_expression())
                continue
            break

        return relational

    def equality_expression(self):
        equality = self.relational_expression()

        while True:
            if self.consume('=='):
                equality = Node('==', type=equality.type, lhs=equality, rhs=self.relational_expression())
                continue
            if self.consume('!='):
                equality = Node('!=', type=equality.type, lhs=equality, rhs=self.relational_expression())
                continue
            break

        return equality

    def and_expression(self):
        and_ = self.equality_expression()

        while True:
            if self.consume('&'):
                and_ = Node('&', type=and_.type, lhs=and_, rhs=self.equality_expression())
                continue
            break

        return and_

    def exclusive_or_expression(self):
        xor = self.and_expression()

        while True:
            if self.consume('^'):
                xor = Node('^', type=xor.type, lhs=xor, rhs=self.and_expression())
                continue
            break

        return xor

    def or_expression(self):
        or_ = self.exclusive_or_expression()

        while True:
            if self.consume('|'):
                or_ = Node('|', type=or_.type, lhs=or_, rhs=self.exclusive_or_expression())
                continue
            break

        return or_

    def logical_and_expression(self):
        land = self.or_expression()

        while True:
            if self.consume('&&'):
                land = Node('&&', type=land.type, lhs=land, rhs=self.or_expression())
                continue
            break

        return land

    def logical_or_expression(self):
        lor = self.logical_and_expression()

        while True:
            if self.consume('||'):
                lor = Node('||', type=lor.type, lhs=lor, rhs=self.logical_and_expression())
                continue
            break

        return lor

    def conditional_expression(self):
        condition = self.logical_or_expression()

        while True:
            break

        return condition

    def assignment_expression(self):
        assign = self.conditional_expression()

        while True:
            break

        return assign

    def expression(self):
        exp = [self.assignment_expression()]

        while True:
            if self.consume(','):
                exp = exp.append(self.assignment_expression())
                continue
            break

        return exp

    def constant_expression(self):
        return self.conditional_expression()


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
