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


t_signed_int = Type('int', signed=True)
n_signed_int_plus1 = Node(ND.INT, type=t_signed_int, val=1)
n_signed_int_minus1 = Node(ND.INT, type=t_signed_int, val=-1)
n_signed_int_0 = Node(ND.INT, type=t_signed_int, val=0)


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
            nodes.append(self.expression())
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
        while True:
            if self.consume('+'):
                unary = self.cast_expression()
                if not unary.type.is_arithmetic():
                    raise ParseError('単行+に非算術型が指定されています')
                continue
            if self.consume('-'):
                node = self.cast_expression()
                if not node.type.is_arithmetic():
                    raise ParseError('単行-に非算術型が指定されています')
                unary = Node('*', type=node.type, lhs=node, rhs=n_signed_int_minus1)
                continue
            if self.consume('!'):
                node = self.cast_expression()
                unary = Node('==', type=t_signed_int, lhs=node, rhs=n_signed_int_0)
                continue
            unary = self.postfix_expression()
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
                rhs = self.cast_expression()
                if not mul.type.is_arithmetic() or not rhs.type.is_arithmetic():
                    raise ParseError('乗法演算子*に算術型以外が指定されています')
                mul = Node('*', type=mul.type, lhs=mul, rhs=rhs)
                continue
            if self.consume('/'):
                rhs = self.cast_expression()
                if not mul.type.is_arithmetic() or not rhs.type.is_arithmetic():
                    raise ParseError('除法演算子/に算術型以外が指定されています')
                mul = Node('/', type=mul.type, lhs=mul, rhs=rhs)
                continue
            if self.consume('%'):
                rhs = self.cast_expression()
                if not mul.type.is_integer() or not rhs.type.is_integer():
                    raise ParseError('剰余演算子%に整数型以外が指定されています')
                mul = Node('%', type=mul.type, lhs=mul, rhs=rhs)
                continue
            break

        return mul

    def additive_expression(self):
        add = self.multiple_expression()

        while True:
            if self.consume('+'):
                rhs = self.multiple_expression()
                # TODO: 片方がポインタならもう片方は整数型 http://port70.net/~nsz/c/c11/n1570.html#6.5.6p2
                if not Type.both_arithmetic(add.type, rhs.type):
                    raise ParseError('加算+に算術型以外が指定されています')
                add = Node('+', type=add.type, lhs=add, rhs=rhs)
                continue
            if self.consume('-'):
                rhs = self.multiple_expression()
                if not Type.both_arithmetic(add.type, rhs.type):
                    raise ParseError('減算-に算術型以外が指定されています')
                add = Node('-', type=add.type, lhs=add, rhs=rhs)
                continue
            break

        return add

    def shift_expression(self):
        shift = self.additive_expression()

        while True:
            if self.consume('>>'):
                rhs = self.additive_expression()
                if not Type.both_integer(shift.type, rhs.type):
                    raise ParseError('右シフト演算子>>に整数型以外が指定されています')
                shift = Node('>>', type=shift.type, lhs=shift, rhs=rhs)
                continue
            if self.consume('<<'):
                rhs = self.additive_expression()
                if not Type.both_integer(shift.type, rhs.type):
                    raise ParseError('左シフト演算子<<に整数型以外が指定されています')
                shift = Node('<<', type=shift.type, lhs=shift, rhs=rhs)
                continue
            break

        return shift

    def relational_expression(self):
        relational = self.shift_expression()

        while True:  # todo: http://port70.net/~nsz/c/c11/n1570.html#6.5.8p2  2番目の制約
            if self.consume('<'):
                rhs = self.shift_expression()
                if not Type.both_real_num(relational.type, rhs.type):
                    raise ParseError('比較演算子<に実数型以外が指定されています')
                relational = Node('<', type=t_signed_int, lhs=relational, rhs=rhs)
                continue
            if self.consume('>'):
                rhs = self.shift_expression()
                if not Type.both_real_num(relational.type, rhs.type):
                    raise ParseError('比較演算子>に実数型以外が指定されています')
                relational = Node('<', type=t_signed_int, rhs=relational, lhs=rhs)
                continue
            if self.consume('<='):
                rhs = self.shift_expression()
                if not Type.both_real_num(relational.type, rhs.type):
                    raise ParseError('比較演算子<=に実数型以外が指定されています')
                relational = Node('<=', type=t_signed_int, lhs=relational, rhs=rhs)
                continue
            if self.consume('>='):
                rhs = self.shift_expression()
                if not Type.both_real_num(relational.type, rhs.type):
                    raise ParseError('比較演算子>=に実数型以外が指定されています')
                relational = Node('<=', type=t_signed_int, rhs=relational, lhs=rhs)
                continue
            break

        return relational

    def equality_expression(self):
        equality = self.relational_expression()

        while True:
            if self.consume('=='):
                rhs = self.relational_expression()
                if not Type.both_arithmetic(equality.type, rhs.type):
                    raise ParseError('比較演算子==に算術型以外が指定されています')
                equality = Node('==', type=t_signed_int, lhs=equality, rhs=rhs)
                continue
            if self.consume('!='):
                rhs = self.relational_expression()
                if not Type.both_arithmetic(equality.type, rhs.type):
                    raise ParseError('比較演算子!=に算術型以外が指定されています')
                equality = Node('!=', type=t_signed_int, lhs=equality, rhs=rhs)
                continue
            break

        return equality

    def and_expression(self):
        and_ = self.equality_expression()

        while True:
            if self.consume('&'):
                rhs = self.equality_expression()
                if not Type.both_integer(and_.type, rhs.type):
                    raise ParseError('&演算子に整数型以外が指定されています')
                and_ = Node('&', type=and_.type, lhs=and_, rhs=rhs)
                continue
            break

        return and_

    def exclusive_or_expression(self):
        xor = self.and_expression()

        while True:
            if self.consume('^'):
                rhs = self.and_expression()
                if not Type.both_integer(xor.type, rhs.type):
                    raise ParseError('^演算子に整数型以外が指定されています')
                xor = Node('^', type=xor.type, lhs=xor, rhs=rhs)
                continue
            break

        return xor

    def or_expression(self):
        or_ = self.exclusive_or_expression()

        while True:
            if self.consume('|'):
                rhs = self.exclusive_or_expression()
                if not Type.both_integer(or_.type, rhs.type):
                    raise ParseError('|演算子に整数型以外が指定されています')
                or_ = Node('|', type=or_.type, lhs=or_, rhs=rhs)
                continue
            break

        return or_

    def logical_and_expression(self):
        land = self.or_expression()

        while True:
            if self.consume('&&'):
                rhs = self.or_expression()
                if not Type.both_integer(land.type, rhs.type):  # TODO: integerじゃなくてscala...
                    raise ParseError('&&演算子に整数型以外が指定されています')
                land = Node('&&', type=land.type, lhs=land, rhs=rhs)
                continue
            break

        return land

    def logical_or_expression(self):
        lor = self.logical_and_expression()

        while True:
            if self.consume('||'):
                rhs = self.logical_and_expression()
                if not Type.both_integer(lor.type, rhs.type):
                    raise ParseError('||演算子に整数型以外が指定されています')
                lor = Node('||', type=lor.type, lhs=lor, rhs=rhs)
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
        exp = self.assignment_expression()

        while True:
            if self.consume(','):
                rhs = self.assignment_expression()
                exp = Node(',', type=rhs.type, lhs=exp, rhs=rhs)
                continue
            break

        return exp

    def constant_expression(self):  # TODO: http://port70.net/~nsz/c/c11/n1570.html#6.6
        return self.conditional_expression()


if __name__ == '__main__':
    from sys import argv
    from tokenizer import Tokenizer

    argc = len(argv)

    if argc > 1:
        if argv[1] == 'test':
            t = Tokenizer()
            tokens = t.tokenize('1 + 2 * 3 & 4')
            print(tokens)
            p = Parser()
            nodes = p.parse(tokens)
            print(nodes)
