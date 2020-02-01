from typing import List

from crawler import Crawler
from nodor import node as node_type
from nodor.node import Node
from .scope import Scope, NotExist


class VarNameError(NameError):
    position: int

    def __init__(self, p: int, *args: str):
        super().__init__(*args)
        self.position = p


class VariableValidator(Crawler[None]):
    scope: Scope

    def __init__(self) -> None:
        self.scope = Scope()

    def integer(self, node: node_type.Integer) -> None:
        return

    def variable(self, node: node_type.Variable) -> None:
        try:
            var = self.scope.exist(node.name)
            node.offset = var.offset
            node.type = var.type
        except NotExist:
            raise VarNameError(node.position, f'name {node.name} is not defined')

    def assign(self, node: node_type.Assign) -> None:
        self.check(node.left)
        self.check(node.right)

    def add(self, node: node_type.Add) -> None:
        self.check(node.left)
        self.check(node.right)

    def mul(self, node: node_type.Mul) -> None:
        self.check(node.left)
        self.check(node.right)
