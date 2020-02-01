from typing import List

from .. import node as node_type
from ..node import Node
from ..type import Int, Type
from crawler import Crawler


class TypingError(Exception):
    node: Node

    def __init__(self, node: Node, *args: str) -> None:
        super().__init__(args)
        self.node = node


class Typor(Crawler[Type]):

    def typing(self, nodes: List[Node]) -> None:
        self.crawl(nodes)

    def integer(self, node: node_type.Integer) -> Type:
        suffix = '' if node.suffix is None else node.suffix.lower()
        signed = 'u' not in suffix
        size = 64 if 'l' in suffix else 32
        ty = Int(size, signed, True, None, None)
        node.type = ty
        return ty

    def variable(self, node: node_type.Variable) -> Type:
        # variableValidateで見てる
        if node.type is None:
            raise TypingError(node, 'no typed variable')
        return node.type

    def assign(self, node: node_type.Assign) -> Type:
        l_type = self.check(node.left)
        r_type = self.check(node.right)

        # TODO: is_assignable

        node.type = l_type
        return l_type

    def add(self, node: node_type.Add) -> Type:
        l_type = self.check(node.left)
        r_type = self.check(node.right)

        if isinstance(l_type, Int) and isinstance(r_type, Int):
            signed = l_type.signed or r_type.signed
            size = max(l_type.size, r_type.size)
            if size is None:
                raise TypingError(node, 'leaf node type.size is None')
            node.type = Int(size, signed, True, None, None)
            return node.type

        raise TypingError(node, 'add; unknown leaf\'s type')

    def mul(self, node: node_type.Mul) -> Type:
        l_type = self.check(node.left)
        r_type = self.check(node.right)

        if isinstance(l_type, Int) and isinstance(r_type, Int):
            signed = l_type.signed or r_type.signed
            size = max(l_type.size, r_type.size)
            if size is None:
                raise TypingError(node, 'leaf node type.size is None')
            node.type = Int(size, signed, True, None, None)
            return node.type

        raise TypingError(node, 'add; unknown leaf\'s type')
