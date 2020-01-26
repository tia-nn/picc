from dataclasses import dataclass
from typing import Union
from .typor.type import Int, Type


# def add_type_field(c: 'Node'):
#     @dataclass
#     class TypedNode(c):
#         type: Type = None
#         __qualname__ = c.__qualname__
#     return TypedNode


# @add_type_field
@dataclass
class Integer:
    value: int
    prefix: str
    suffix: str
    type: 'Int' = None

    def __str__(self):
        return str(self.type) + ' ' + str(self.value)

    def __repr__(self):
        return str(self)


@dataclass
class BinaryOperator:
    left: 'Node'
    right: 'Node'
    type: 'Type' = None

    def __str__(self):
        return '((' + str(self.type) + ')' + str(self.left) + ' + ' + str(self.right) + ')'

    def __repr__(self):
        return str(self)


@dataclass
class Add(BinaryOperator):
    pass


@dataclass
class Mul(BinaryOperator):
    pass


Node = Union[Integer, Add, Mul]

Number = Union[Integer]
Expression = Union[Number, Add, Mul]
