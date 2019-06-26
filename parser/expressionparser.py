from typing import List, Union, Dict, Tuple, Any

from type import Type
from tokenizer import TK, Token
from utils import debug, warning

from parser.parseutils import *
from parser.tokenparser import TokenParser


class ExpressionParser(TokenParser):
    # expression

    def primary_expression(self) -> Node:
        try:
            return self.constant()
        except ParseError:
            pass
        if self.consume('('):
            expression = self.expression()
            self.consume_must(')')
            return expression
        raise ParseError

    def postfix_expression(self) -> Node:
        postfix = self.primary_expression()

        while True:

            if self.consume('('):
                if postfix.type.ty == '.unknown':
                    warning(postfix.val, '関数の暗黙的宣言(返り値をlongにします)')
                    postfix.type = Type('.func', func_call_to=Type('long', signed=True))
                args = self.sep_repeat(self.assignment_expression, ',', True)
                self.consume_must(')')
                if not postfix.type.is_func:
                    raise TypeError('関数以外を呼び出そうとしています')
                postfix = Node(ND.CALL, type=postfix.type.func_call_to, call=postfix, call_args=args)
                continue

            break

        if postfix.type.ty == '.unknown':
            raise TypeError('変数が宣言されていません')

        return postfix

    def unary_expression(self) -> Node:
        unary = None

        while True:
            if self.consume('+'):
                unary = self.cast_expression()
                if not unary.type.is_arithmetic():
                    raise TypeError('単行+に非算術型が指定されています')
                continue
            if self.consume('-'):
                node = self.cast_expression()
                if not node.type.is_arithmetic():
                    raise TypeError('単行-に非算術型が指定されています')
                unary = Node('*', type=node.type, lhs=node, rhs=n_signed_int_minus1)
                continue
            if self.consume('!'):
                node = self.cast_expression()
                unary = Node('==', type=t_signed_int, lhs=node, rhs=n_signed_int_0)
                continue
            break

        if unary is None:
            unary = self.postfix_expression()
        return unary

    def cast_expression(self) -> Node:
        cast = self.unary_expression()

        while True:
            break

        return cast

    def multiple_expression(self) -> Node:
        mul = self.cast_expression()

        while True:
            if self.consume('*'):
                rhs = self.cast_expression()
                if not mul.type.is_arithmetic() or not rhs.type.is_arithmetic():
                    raise TypeError('乗法演算子*に算術型以外が指定されています')
                mul = Node('*', type=mul.type, lhs=mul, rhs=rhs)
                continue
            if self.consume('/'):
                rhs = self.cast_expression()
                if not mul.type.is_arithmetic() or not rhs.type.is_arithmetic():
                    raise TypeError('除法演算子/に算術型以外が指定されています')
                mul = Node('/', type=mul.type, lhs=mul, rhs=rhs)
                continue
            if self.consume('%'):
                rhs = self.cast_expression()
                if not mul.type.is_integer() or not rhs.type.is_integer():
                    raise TypeError('剰余演算子%に整数型以外が指定されています')
                mul = Node('%', type=mul.type, lhs=mul, rhs=rhs)
                continue
            break

        return mul

    def additive_expression(self) -> Node:
        add = self.multiple_expression()

        while True:
            if self.consume('+'):
                rhs = self.multiple_expression()
                # TODO: 片方がポインタならもう片方は整数型 http://port70.net/~nsz/c/c11/n1570.html#6.5.6p2
                if not Type.both_arithmetic(add.type, rhs.type):
                    debug(add.type)
                    raise TypeError('加算+に算術型以外が指定されています')
                add = Node('+', type=add.type, lhs=add, rhs=rhs)
                continue
            if self.consume('-'):
                rhs = self.multiple_expression()
                if not Type.both_arithmetic(add.type, rhs.type):
                    raise TypeError('減算-に算術型以外が指定されています')
                add = Node('-', type=add.type, lhs=add, rhs=rhs)
                continue
            break

        return add

    def shift_expression(self) -> Node:
        shift = self.additive_expression()

        while True:
            if self.consume('>>'):
                rhs = self.additive_expression()
                if not Type.both_integer(shift.type, rhs.type):
                    raise TypeError('右シフト演算子>>に整数型以外が指定されています')
                shift = Node('>>', type=shift.type, lhs=shift, rhs=rhs)
                continue
            if self.consume('<<'):
                rhs = self.additive_expression()
                if not Type.both_integer(shift.type, rhs.type):
                    raise TypeError('左シフト演算子<<に整数型以外が指定されています')
                shift = Node('<<', type=shift.type, lhs=shift, rhs=rhs)
                continue
            break

        return shift

    def relational_expression(self) -> Node:
        relational = self.shift_expression()

        while True:  # todo: http://port70.net/~nsz/c/c11/n1570.html#6.5.8p2  2番目の制約
            if self.consume('<'):
                rhs = self.shift_expression()
                if not Type.both_real_num(relational.type, rhs.type):
                    raise TypeError('比較演算子<に実数型以外が指定されています')
                relational = Node('<', type=t_signed_int, lhs=relational, rhs=rhs)
                continue
            if self.consume('>'):
                rhs = self.shift_expression()
                if not Type.both_real_num(relational.type, rhs.type):
                    raise TypeError('比較演算子>に実数型以外が指定されています')
                relational = Node('<', type=t_signed_int, rhs=relational, lhs=rhs)
                continue
            if self.consume('<='):
                rhs = self.shift_expression()
                if not Type.both_real_num(relational.type, rhs.type):
                    raise TypeError('比較演算子<=に実数型以外が指定されています')
                relational = Node('<=', type=t_signed_int, lhs=relational, rhs=rhs)
                continue
            if self.consume('>='):
                rhs = self.shift_expression()
                if not Type.both_real_num(relational.type, rhs.type):
                    raise TypeError('比較演算子>=に実数型以外が指定されています')
                relational = Node('<=', type=t_signed_int, rhs=relational, lhs=rhs)
                continue
            break

        return relational

    def equality_expression(self) -> Node:
        equality = self.relational_expression()

        while True:
            if self.consume('=='):
                rhs = self.relational_expression()
                if not Type.both_arithmetic(equality.type, rhs.type):
                    raise TypeError('比較演算子==に算術型以外が指定されています')
                equality = Node('==', type=t_signed_int, lhs=equality, rhs=rhs)
                continue
            if self.consume('!='):
                rhs = self.relational_expression()
                if not Type.both_arithmetic(equality.type, rhs.type):
                    raise TypeError('比較演算子!=に算術型以外が指定されています')
                equality = Node('!=', type=t_signed_int, lhs=equality, rhs=rhs)
                continue
            break

        return equality

    def and_expression(self) -> Node:
        and_ = self.equality_expression()

        while True:
            if self.consume('&'):
                rhs = self.equality_expression()
                if not Type.both_integer(and_.type, rhs.type):
                    raise TypeError('&演算子に整数型以外が指定されています')
                and_ = Node('&', type=and_.type, lhs=and_, rhs=rhs)
                continue
            break

        return and_

    def exclusive_or_expression(self) -> Node:
        xor = self.and_expression()

        while True:
            if self.consume('^'):
                rhs = self.and_expression()
                if not Type.both_integer(xor.type, rhs.type):
                    raise TypeError('^演算子に整数型以外が指定されています')
                xor = Node('^', type=xor.type, lhs=xor, rhs=rhs)
                continue
            break

        return xor

    def or_expression(self) -> Node:
        or_ = self.exclusive_or_expression()

        while True:
            if self.consume('|'):
                rhs = self.exclusive_or_expression()
                if not Type.both_integer(or_.type, rhs.type):
                    raise TypeError('|演算子に整数型以外が指定されています')
                or_ = Node('|', type=or_.type, lhs=or_, rhs=rhs)
                continue
            break

        return or_

    def logical_and_expression(self) -> Node:
        land = self.or_expression()

        while True:
            if self.consume('&&'):
                rhs = self.or_expression()
                if not Type.both_integer(land.type, rhs.type):  # TODO: integerじゃなくてscala...
                    raise TypeError('&&演算子に整数型以外が指定されています')
                land = Node('&&', type=land.type, lhs=land, rhs=rhs)
                continue
            break

        return land

    def logical_or_expression(self) -> Node:
        lor = self.logical_and_expression()

        while True:
            if self.consume('||'):
                rhs = self.logical_and_expression()
                if not Type.both_integer(lor.type, rhs.type):
                    raise TypeError('||演算子に整数型以外が指定されています')
                lor = Node('||', type=lor.type, lhs=lor, rhs=rhs)
                continue
            break

        return lor

    def conditional_expression(self) -> Node:
        condition = self.logical_or_expression()

        while True:
            break

        return condition

    def assignment_expression(self) -> Node:
        assign = self.conditional_expression()

        while True:
            if self.consume('='):
                if assign.type.const:
                    raise TypeError('const変数に代入しています')
                assign = Node('=', type=assign.type, lhs=assign, rhs=self.assignment_expression())
            break

        return assign

    def expression(self) -> Node:
        exp = self.assignment_expression()

        while True:
            if self.consume(','):
                rhs = self.assignment_expression()
                exp = Node(',', type=rhs.type, lhs=exp, rhs=rhs)
                continue
            break

        return exp

    def constant_expression(self) -> Node:  # TODO: http://port70.net/~nsz/c/c11/n1570.html#6.6
        constant = self.conditional_expression()

        def gen_constant(node):
            if node.ty == ND.INT:
                return node.val
            if node.ty == '*':
                return gen_constant(node.lhs) * gen_constant(node.rhs)
            if node.ty == '/':
                return gen_constant(node.lhs) // gen_constant(node.rhs)
            if node.ty == '%':
                return gen_constant(node.lhs) % gen_constant(node.rhs)
            if node.ty == '+':
                return gen_constant(node.lhs) + gen_constant(node.rhs)
            if node.ty == '-':
                return gen_constant(node.lhs) - gen_constant(node.rhs)
            if node.ty == '<<':
                return gen_constant(node.lhs) << gen_constant(node.rhs)
            if node.ty == '>>':
                return gen_constant(node.lhs) >> gen_constant(node.rhs)
            if node.ty == '<':
                return int(gen_constant(node.lhs) < gen_constant(node.rhs))
            if node.ty == '>':
                return int(gen_constant(node.lhs) > gen_constant(node.rhs))
            if node.ty == '<=':
                return int(gen_constant(node.lhs) <= gen_constant(node.rhs))
            if node.ty == '>=':
                return int(gen_constant(node.lhs) >= gen_constant(node.rhs))
            if node.ty == '==':
                return int(gen_constant(node.lhs) == gen_constant(node.rhs))
            if node.ty == '!=':
                return int(gen_constant(node.lhs) != gen_constant(node.rhs))
            if node.ty == '&':
                return int(gen_constant(node.lhs) & gen_constant(node.rhs))
            if node.ty == '|':
                return int(gen_constant(node.lhs) | gen_constant(node.rhs))
            if node.ty == '&&':
                return 1 if gen_constant(node.lhs) and gen_constant(node.rhs) else 0
            if node.ty == '|':
                return 1 if gen_constant(node.lhs) or gen_constant(node.rhs) else 0

        res = gen_constant(constant)
        return Node(ND.INT, type=t_signed_int, val=res)
