from typing import List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum, auto

TYPES = '.ptr', '.func', 'void', 'char', 'short', 'int', 'long', 'long long', 'float', 'double', '_Bool', '_Complex'
STORAGE_CLASS_SPECIFIER = 'typedef', 'extern', 'static', '_Thread_local', 'auto', 'register'
TYPE_SPECIFIER = 'void', 'char', 'short', 'int', 'long', 'float', 'double', \
                 'signed', 'unsigned', '_Bool', '_Complex'
TYPE_QUALIFIER = 'const', 'restrict', 'volatile', '_Atomic'
FUNCTION_SPECIFIER = 'inline', '_Noreturn'

ARITHMETIC_TYPE = 'short', 'int', 'long', 'long long', 'float', 'double'
INTEGER_TYPE = 'short', 'int', 'long', 'long long'
REAL_NUMBER_TYPE = 'short', 'int', 'long', 'long long', 'float', 'double'

TYPE_SIZE = {
    '.ptr': 8,
    'void': 8,
    'char': 1,
    'short': 4,
    'int': 4,
    'long': 8,
    'long long': 16,
    'float': 8,
    'double': 16,
    '.func': 0,
}


@dataclass
class Type:
    ty: str
    signed: bool = None
    ptr_to: 'Type' = None
    array_size: int = None
    storage_class: str = None
    thread_local: bool = None
    const: bool = None
    restrict: bool = None
    volatile: bool = None
    atomic: bool = None
    inline: bool = None
    noreturn: bool = None
    func_call_to: 'Type' = None
    param_list: List[Tuple['Type', Optional[str]]] = None

    def is_arithmetic(self):
        return self.ty in ARITHMETIC_TYPE

    def is_integer(self):
        return self.ty in INTEGER_TYPE

    def is_real_num(self):
        return self.ty in REAL_NUMBER_TYPE

    @staticmethod
    def both_arithmetic(a: 'Type', b: 'Type'):
        return a.is_arithmetic() and b.is_arithmetic()

    @staticmethod
    def both_integer(a: 'Type', b: 'Type'):
        return a.is_integer() and b.is_integer()

    @staticmethod
    def both_real_num(a: 'Type', b: 'Type'):
        return a.is_real_num() and b.is_real_num()

    @property
    def size(self):
        return TYPE_SIZE[self.ty]

    @property
    def is_func(self):
        return self.ty == '.func'

    @property
    def is_ptr(self):
        return self.ty in ('.ptr', )

    def __repr__(self):
        fs = ('ty', 'signed', 'ptr_to', 'array_size', 'storage_class', 'thread_local',
              'const', 'restrict', 'volatile', 'atomic', 'inline', 'noreturn',
              'func_call_to', 'param_list')
        fs = (i for i in fs if getattr(self, i) is not None)
        return f'[{" ".join([i+"="+repr(getattr(self, i)) for i in fs])}]'

