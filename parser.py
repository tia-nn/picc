from typing import List, Union, Dict, Tuple
from dataclasses import dataclass
from enum import Enum, auto
from collections import deque

from type import Type
from tokenizer import TK, Token
from utils import debug, warning


TYPES = 'void', 'char', 'short', 'int', 'long', 'long long', 'float', 'double', '_Bool', '_Complex'
STORAGE_CLASS_SPECIFIER = 'typedef', 'extern', 'static', '_Thread_local', 'auto', 'register'
TYPE_SPECIFIER = 'void', 'char', 'short', 'int', 'long', 'float', 'double', \
                 'signed', 'unsigned', '_Bool', '_Complex'
TYPE_QUALIFIER = 'const', 'restrict', 'volatile', '_Atomic'
FUNCTION_SPECIFIER = 'inline', '_Noreturn'


class ParseError(Exception):
    pass


class ND(Enum):
    INT = auto()
    IDE = auto()
    DECL = auto()


@dataclass
class Node:
    ty: Union[ND, str]
    type: Type
    val: Union[int, str] = None
    lhs: 'Node' = None
    rhs: 'Node' = None
    d_init_list: List['Node'] = None


t_signed_int = Type('int', signed=True)
n_signed_int_plus1 = Node(ND.INT, type=t_signed_int, val=1)
n_signed_int_minus1 = Node(ND.INT, type=t_signed_int, val=-1)
n_signed_int_0 = Node(ND.INT, type=t_signed_int, val=0)


class ParseUtils:
    p: int
    tokens: List[Token]
    variables: Dict[str, Type]
    offset: Dict[str, int]

    # utils

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
        raise ParseError

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

    # sub parser

    @staticmethod
    def make_type(decl_specs):
        t = Type(None)
        types = deque()

        not_arithmetic = False
        short = False
        long = False
        long2 = False
        ty = None

        for s in decl_specs:
            if s in ('signed', 'unsigned'):
                if t.signed is not None:
                    raise ParseError('signed, unsignedが複数指定されています')
                t.signed = s == 'signed'
                continue
            if s == '_Thread_local':
                if t.thread_local is not None:
                    raise ParseError('_Thread_localが複数あります')
                t.thread_local = True
                continue
            if s == 'const':
                if t.const is not None:
                    raise ParseError('constが複数あります')
                t.const = True
                continue
            if s == 'restrict':
                if t.restrict is not None:
                    raise ParseError('restrictが複数あります')
                t.restrict = True
                continue
            if s == 'volatile':
                if t.volatile is not None:
                    raise ParseError('volatileが複数あります')
                t.volatile = True
                continue
            if s == '_Atomic':
                if t.atomic is not None:
                    raise ParseError('_Atomicが複数あります')
                t.atomic = True
                continue
            if s == 'inline':
                if t.inline is not None:
                    raise ParseError('inlineが複数あります')
                t.inline = True
                continue
            if s == '_Noreturn':
                if t.noreturn is not None:
                    raise ParseError('_Noreturnが複数あります')
                t.noreturn = True
                continue
            if s in STORAGE_CLASS_SPECIFIER:
                if t.storage_class is not None:
                    raise ParseError('記憶域クラス指定子が複数指定されています')
                t.storage_class = s
                continue
            if s in TYPE_SPECIFIER:
                if s in ('void', 'char', ):
                    t.ty = s
                    not_arithmetic = True
                    continue
                if s == 'long':
                    if long:
                        if long2:
                            raise ParseError('longが3つ以上指定されています')
                        long2 = True
                        continue
                    long = True
                    continue
                if s == 'short':
                    if short:
                        raise ParseError('shortが複数指定されています')
                    short = True
                    continue
                if ty is not None:
                    raise ParseError('型が複数指定されています')
                ty = s
                continue
            raise TypeError('error1')

        if not_arithmetic and (long or short):
            raise ParseError('非算術型にlong|shortを指定しています')
        if long and short:
            raise TypeError('longとshortが同時に指定されています')

        if not long and not short:
            t.ty = 'int'
            return t

        if short:
            t.ty = 'short'
            return t

        if long2:
            t.ty = 'long long'
            return t

        if long:
            t.ty = 'long'
            return t

        raise TypeError('error2')


class TokenParser(ParseUtils):
    # lexical-element

    def constant(self):
        if self.next_is(TK.NUM):
            t = self.pos()
            return Node(ND.INT, type=t.type, val=t.val)
        if self.next_is(TK.IDE):
            t = self.pos()
            return Node(ND.IDE, type=self.variables[t.val], val=t.val)
        raise ParseError

    def identifier(self):
        if self.next_is(TK.IDE):
            return self.pos().val
        raise ParseError


class ExpressionParser(TokenParser):
    # expression

    def primary_expression(self):
        try:
            return self.constant()
        except ParseError:
            pass
        if self.consume('('):
            expression = self.expression()
            self.consume_must(')')
            return expression
        raise ParseError

    def postfix_expression(self):
        postfix = self.primary_expression()

        while True:
            break

        return postfix

    def unary_expression(self):
        unary = None

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
            break

        if unary is None:
            unary = self.postfix_expression()
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
            if self.consume('='):
                if assign.type.const:
                    raise TypeError('const変数に代入しています')
                assign = Node('=', type=assign.type, lhs=assign, rhs=self.assignment_expression())
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


class DeclarationParser(ExpressionParser):
    # declaration

    def declaration(self):
        return self.caller(
            self._declaration_1,
            self._declaration_2
        )

    def _declaration_1(self):
        declaration_specifiers = self.declaration_specifiers()
        t = self.make_type(declaration_specifiers)
        init_declarator_list = self.select(lambda: self.init_declarator_list(t))
        if init_declarator_list is None:
            init_declarator_list = []
        self.consume_must(';')

        init_list = []
        for name, init in init_declarator_list:
            if init is not None:
                init_list.append(Node('=', type=t, lhs=Node(ND.IDE, type=t, val=name), rhs=init[0]))

        return Node(ND.DECL, type=t, val=init_declarator_list, d_init_list=init_list)

    def _declaration_2(self):
        raise ParseError

    def init_declarator_list(self, t):
        init_declarator_list = [self.init_declarator(t)]

        while True:
            if self.consume(','):
                init_declarator_list.append(self.init_declarator(t))
                continue
            break

        return init_declarator_list

    def init_declarator(self, t) -> Tuple[Union[int, str], List[Node]]:
        declarator = self.declarator()

        initializer = None
        if self.consume('='):
            initializer = self.initializer()

        # 内部的変数宣言
        self.variables[declarator] = t
        self.offset[declarator] = max(self.offset.values() or [0]) + t.size

        if t.const and initializer is None:
            warning('const宣言で初期化されていません')

        return declarator, initializer

    def declarator(self):
        try:
            pointer = self.pointer()
        except ParseError:
            pointer = None
        direct_declarator = self.direct_declarator()
        return direct_declarator

    def direct_declarator(self):
        direct_declarator = None

        try:
            direct_declarator = self.identifier()
        except ParseError:
            pass

        while True:
            break

        if direct_declarator is None:
            raise ParseError

        return direct_declarator

    def initializer(self):
        if self.consume('{'):
            pass

        initializer = [self.assignment_expression()]

        return initializer

    def pointer(self):
        raise ParseError

    """

    def direct_abstract_declarator(self):
        direct_abstract_declarator = None
        if self.consume('('):
            direct_abstract_declarator = self.abstract_declarator()
            self.consume_must(')')

        while True:
            break

        if direct_abstract_declarator is None:
            raise ParseError

        return direct_abstract_declarator

    def initializer(self):
        try:
            return self.assignment_expression()
        except ParseError:
            pass
        if self.consume('{'):
            initializer_list = self.initializer_list()
            self.consume(',')
            self.consume_must('}')
            return initializer_list

        raise ParseError

    def initializer_list(self):
        initializer_list = [self._initializer_list()]

        while True:
            try:
                initializer_list.append(self._initializer_list())
            except ParseError:
                break

        return initializer_list

    def _initializer_list(self):
        try:
            designation = self.designation()
        except ParseError:
            designation = None

        initializer = self.initializer()

        return designation, initializer

    def designation(self):
        designator_list = self.designator_list()
        self.consume_must('=')
        return designator_list

    def designator_list(self):
        designator_list = [self.designator()]

        while True:
            try:
                designator_list.append(self.designator())
            except ParseError:
                break

        return designator_list

    def designator(self):
        if self.consume('['):
            constant_expression = self.constant_expression()
            self.consume_must(']')
            #todo
            return
        if self.consume('.'):
            return self.identifier()
        raise ParseError

    """

    def declaration_specifiers(self):
        return self.repeat(self.declaration_specifier, False)

    def declaration_specifier(self):
        return self.caller(
            self.storage_class_specifier,
            self.type_specifier,
            self.type_qualifier,
            self.function_specifier,

        )

    def storage_class_specifier(self):
        return self.token_consumer(STORAGE_CLASS_SPECIFIER)

    def type_specifier(self):
        return self.token_consumer(TYPE_SPECIFIER)
        # TODO: atomic, struct, enum, typedef

    def type_qualifier(self):
        return self.token_consumer(TYPE_QUALIFIER)

    def function_specifier(self):
        return self.token_consumer(FUNCTION_SPECIFIER)


class StatementParser(DeclarationParser):
    def statement(self):
        try:
            statement = self.expression()
        except ParseError:
            pass
        else:
            self.consume_must(';')
            return statement
        try:
            statement = self.declaration()
        except ParseError:
            pass
        else:
            return statement

        raise ParseError


class Parser(StatementParser):

    def parse(self, tokens):
        self.p = 0
        nodes = []
        self.variables = {}
        self.offset = {}
        self.tokens = tokens
        while not self.consume(TK.EOF):
            nodes.append(self.statement())
        return nodes


if __name__ == '__main__':
    from sys import argv
    from tokenizer import Tokenizer

    argc = len(argv)

    if argc > 1:
        if argv[1] == 'test':
            t = Tokenizer()
            tokens = t.tokenize('3u * -7')
            print(tokens)
            p = Parser()
            nodes = p.parse(tokens)
            print(nodes)
