from typing import List, Optional, Union
from enum import Enum, auto
from dataclasses import dataclass
from collections import Counter
from abc import ABCMeta, abstractmethod
from collections import namedtuple


__all__ = ['storage_class', 'QUALIFIER', 'Int']


storage_class = namedtuple('storage_class', ('typedef', 'extern', 'static', 'thread_local', 'auto', 'register'))


class QUALIFIER(Enum):
    const = auto()
    restrict = auto()
    volatile = auto()
    atomic = auto()


# types

class StorageClass(metaclass=ABCMeta):
    typedef: bool = False
    extern: bool = False
    static: bool = False
    thread_local: bool = False
    auto: bool = True
    register: bool = False

    def set_storage_class(self, sc: storage_class):
        self.typedef = sc.typedef
        self.extern = sc.extern
        self.static = sc.static
        self.thread_local = sc.thread_local
        self.auto = sc.auto
        self.register = sc.register

    def __str__(self):
        typedef = 'typedef' if self.typedef else ''
        extern = 'extern' if self.extern else ''
        static = 'static' if self.static else ''
        thread_local = '_Thread local' if self.thread_local else ''
        auto = 'auto' if self.auto else ''
        register = 'register' if self.register else ''
        return ' '.join([i for i in (typedef, extern, static, thread_local, auto, register) if i])


class Qualifier(metaclass=ABCMeta):
    const: bool = False
    restrict: bool = False
    volatile: bool = False
    atomic: bool = False

    def set_qualifier(self, q: QUALIFIER):
        if q == QUALIFIER.const:
            self.const = True
        elif q == QUALIFIER.restrict:
            self.restrict = True
        elif q == QUALIFIER.volatile:
            self.volatile = True
        elif q == QUALIFIER.atomic:
            self.atomic = True

        if not self.qualifier_validate():
            raise ValueError('qualifier is only one')

    def qualifier_validate(self) -> bool:
        if [self.const, self.restrict, self.volatile, self.atomic].count(True) > 1:
            return False
        return True

    def __str__(self):
        if self.const:
            return 'const'
        if self.restrict:
            return 'restrict'
        if self.volatile:
            return 'volatile'
        if self.atomic:
            return '_Atomic'
        return ''


class Align(metaclass=ABCMeta):
    alignas: bool = False
    type_name: str = None
    constant_expression: 'Node' = None


class Base(StorageClass, Qualifier, Align, metaclass=ABCMeta):
    size: int = None
    is_literal = False


class Arithmetic(Base, metaclass=ABCMeta):
    signed: bool = True


class Int(Arithmetic):

    def __init__(self, size: int, signed: bool, is_literal, storage_classes: Optional[storage_class], qualifier: Optional[QUALIFIER], align: Optional[Union[str, 'Node']] = None):
        self.size = size
        self.signed = signed
        self.is_literal = is_literal
        if not is_literal:
            self.set_storage_class(storage_classes)
            self.set_qualifier(qualifier)

    def __str__(self):
        if not self.is_literal:
            storage = StorageClass.__str__(self)
            qual = Qualifier.__str__(self)
        else:
            storage = ''
            qual = 'literal'
        u = '' if self.signed else 'u'
        size = str(self.size)

        return ' '.join([i for i in (qual, storage, u + 'int' + size + '_t') if i])

    def __repr__(self):
        return str(self)


# from ..node import Node