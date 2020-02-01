from typing import List, Deque
from dataclasses import dataclass
from collections import deque

from ..type import Type, Int, storage_class, QUALIFIER
from ..node import Variable


Block = List[Variable]


class NotExist(Exception):
    pass


class Scope:
    scope: Deque[Block]

    def __init__(self):
        from string import ascii_lowercase
        self.scope = deque()
        self.scope.append([])
        self.scope[0].append(Variable(0, 'aa', 4, Int(32, True, False, storage_class(False, False, False, False, True, False), None)))
        for i, v in enumerate(ascii_lowercase[1:]):
            self.scope[0].append(Variable(0, v*2, (i + 1) * 8 + 4, Int(64, True, False, storage_class(False, False, False, False, True, False), None)))

    def exist(self, name) -> Variable:
        for block in list(self.scope)[::-1]:
            if (v := self.is_exist(block, name)):
                return v
        raise NotExist

    @staticmethod
    def is_exist(block: Block, name: str) -> Variable:
        for v in block:
            if v.name == name:
                return v
        raise NotExist
