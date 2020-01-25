from dataclasses import dataclass
from typing import Union
from .typor.type import Int


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


Number = Union[Integer]

Node = Union[Number]
