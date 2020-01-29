from typing import List

from crawler import Crawler
from nodor import node as node_type
from nodor.node import Node
from .scope import Scope, NotExist


class VarNameError(NameError):
    p: int

    def __init__(self, p, *args):
        super().__init__(*args)
        self.p = p


class VariableValidator(Crawler):
    scope: Scope

    def __init__(self):
        self.scope = Scope()

    def integer(self, node: node_type.Integer):
        return

    def variable(self, node: node_type.Variable):
        try:
            var = self.scope.exist(node.name)
            node.offset = var.offset
            node.type = var.type
        except NotExist:
            raise VarNameError(node.position, f'name {node.name} is not defined')
