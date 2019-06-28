from typing import List, Union, Dict, Tuple, Any, Deque
from enum import Enum, auto
from dataclasses import dataclass
from collections import deque

from type import Type
from tokenizer import TK, Token
from utils import debug, warning


TYPES = '.func', 'void', 'char', 'short', 'int', 'long', 'long long', 'float', 'double', '_Bool', '_Complex'
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
    CALL = auto()
    UNKNOWN = auto()
    DEF = auto()
    BLOCK = auto()
    NONE = auto()
    EXP = auto()


@dataclass
class Node:
    ty: Union[ND, str]
    type: Type = None
    val: Union[int, str] = None
    lhs: 'Node' = None
    rhs: 'Node' = None
    condition: 'Node' = None
    init: 'Node' = None
    proc: 'Node' = None
    d_init_list: List['Node'] = None
    call: 'Node' = None
    call_args: List['Node'] = None
    stmts: List['Node'] = None
    block: 'Node' = None
    else_block: 'Node' = None
    scope: 'Scope' = None
    args: Dict[str, Tuple[Type, int]] = None


@dataclass
class InnerNode:
    ty: Union[ND, str]
    list: List[Any]
    name: str


t_signed_int = Type('int', signed=True)
n_signed_int_plus1 = Node(ND.INT, type=t_signed_int, val=1)
n_signed_int_minus1 = Node(ND.INT, type=t_signed_int, val=-1)
n_signed_int_0 = Node(ND.INT, type=t_signed_int, val=0)


class Scope:
    _scope: Deque[Dict[str, Tuple[Type, int]]]

    def __init__(self):
        self._scope = deque([{}])

    def get(self, name) -> Tuple[Type, int]:
        for i in reversed(self._scope):
            if name in i:
                return i[name]

        raise TypeError('変数が宣言されていません')

    def new_scope(self):
        self._scope.append({})

    def set_var(self, name: str, ty: Type):
        self._scope[-1][name] = ty, self.max_offset() + ty.size

    def max_offset(self) -> int:
        a = [[j[1] for j in i.values()] for i in self._scope]
        b = [0]
        for i in a:
            b += i

        return max([k for k in b])

    def pop_scope(self):
        return self._scope.pop()

    def push_scope(self, scope):
        self._scope.append(scope)


class ParseUtils:
    p: int
    tokens: List[Token]
    variables: Scope

    # utils

    def pos(self) -> Token:
        ret = self.tokens[self.p]
        self.p += 1
        return ret

    def next_is(self, ty) -> bool:
        return self.tokens[self.p].ty == ty

    def next_in(self, tys) -> bool:
        return self.tokens[self.p].ty in tys

    def consume(self, ty) -> bool:
        if self.next_is(ty):
            self.p += 1
            return True
        return False

    def consume_must(self, ty) -> Token:
        if self.next_is(ty):
            return self.pos()
        raise TypeError

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

    def sep_repeat(self, method, sep, allow_null=False):
        try:
            ret = [method()]
        except ParseError:
            if allow_null:
                return []
            raise
        while True:
            if self.consume(sep):
                try:
                    ret.append(method())
                except ParseError:
                    self.p -= 1
                    break
                continue
            break

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
        types = []

        not_arithmetic = False
        short = False
        long = False
        long2 = False
        ty = None

        for s in decl_specs:
            if s in ('signed', 'unsigned'):
                if t.signed is not None:
                    raise TypeError('signed, unsignedが複数指定されています')
                t.signed = s == 'signed'
                continue
            if s == '_Thread_local':
                if t.thread_local is not None:
                    raise ParseError('_Thread_localが複数あります')
                t.thread_local = True
                continue
            if s == 'const':
                if t.const is not None:
                    raise TypeError('constが複数あります')
                t.const = True
                continue
            if s == 'restrict':
                if t.restrict is not None:
                    raise TypeError('restrictが複数あります')
                t.restrict = True
                continue
            if s == 'volatile':
                if t.volatile is not None:
                    raise TypeError('volatileが複数あります')
                t.volatile = True
                continue
            if s == '_Atomic':
                if t.atomic is not None:
                    raise TypeError('_Atomicが複数あります')
                t.atomic = True
                continue
            if s == 'inline':
                if t.inline is not None:
                    raise TypeError('inlineが複数あります')
                t.inline = True
                continue
            if s == '_Noreturn':
                if t.noreturn is not None:
                    raise TypeError('_Noreturnが複数あります')
                t.noreturn = True
                continue
            if s in STORAGE_CLASS_SPECIFIER:
                if t.storage_class is not None:
                    raise TypeError('記憶域クラス指定子が複数指定されています')
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
            raise TypeError('非算術型にlong|shortを指定しています')
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


if __name__ == '__main__':
    scope = Scope()

    scope.set_var('a', Type('int'))
    scope.set_var('b', Type('int'))

    print(scope.get('b'))

    scope.new_scope()
    scope.set_var('b', Type('long'))

    print(scope.get('b'))

    print(scope._scope)

    print(scope.pop_scope())

    print(scope.get('b'))

    print(scope._scope)
