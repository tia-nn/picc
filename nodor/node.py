from dataclasses import dataclass
from typing import Union, Optional
from .type import Int, Type
from abc import ABCMeta, abstractmethod


@dataclass
class BaseNode(metaclass=ABCMeta):
    position: int


@dataclass
class Integer(BaseNode):
    value: int
    prefix: str
    suffix: str
    type: Optional[Int] = None

    def __str__(self):
        return str(self.type) + ' ' + str(self.value)

    def __repr__(self):
        return str(self)


@dataclass
class Variable(BaseNode):
    name: str
    offset: Optional[int] = None
    type: Optional[Type] = None

    def __str__(self):
        return f'{str(self.type) if self.type is not None else "nonTyped"} {self.name}'

    def __repr__(self):
        return str(self)


@dataclass  # type: ignore  # abs method in dataclass is invalid in mypy...
class BinaryOperator(BaseNode, metaclass=ABCMeta):
    left: 'Expression'
    right: 'Expression'
    type: Optional[Type] = None

    @property
    @abstractmethod
    def _operator(self):
        raise NotImplementedError

    def __str__(self):
        return '((' + str(self.type) + ')' + str(self.left) + f' {self._operator} ' + str(self.right) + ')'

    def __repr__(self):
        return str(self)


@dataclass
class Add(BinaryOperator):
    _operator: str = '+'


@dataclass
class Mul(BinaryOperator):
    _operator: str = '*'


@dataclass
class Assign(BinaryOperator):
    _operator: str = '='


Node = Union[Integer, Variable, Assign, Add, Mul]

Number = Union[Integer]
PrimaryExpression = Union[Number, Variable]
Expression = Union[PrimaryExpression, Assign, Add, Mul]
Statement = Union[Expression]
