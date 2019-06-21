from typing import List
from dataclasses import dataclass
from enum import Enum, auto

TYPES = 'void', 'char', 'short', 'int', 'long', 'long long', 'float', 'double', '_Bool', '_Complex'
STORAGE_CLASS_SPECIFIER = 'typedef', 'extern', 'static', '_Thread_local', 'auto', 'register'
TYPE_SPECIFIER = 'void', 'char', 'short', 'int', 'long', 'float', 'double', \
                 'signed', 'unsigned', '_Bool', '_Complex'
TYPE_QUALIFIER = 'const', 'register', 'volatile', '_Atomic'
FUNCTION_SPECIFIER = 'inline', '_Noreturn'


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

    def __repr__(self):
        fs = ('ty', 'signed', 'ptr_to', 'array_size', 'storage_class', 'thread_local',
              'const', 'restrict', 'volatile', 'atomic', 'inline', 'noreturn')
        fs = (i for i in fs if getattr(self, i) is not None)
        return f'[{" ".join([i+"="+repr(getattr(self, i)) for i in fs])}]'

