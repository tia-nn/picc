from typing import List

from .. import node as node_type, Node
from ..type import Int
from crawler import Crawler


class TypingError(Exception):
    node: Node

    def __init__(self, node: Node, *args):
        super().__init__(args)
        self.node = node


class Typor(Crawler):

    def typing(self, nodes: List) -> None:
        self.crawl(nodes)

    def integer(self, node: node_type.Integer):
        suffix = '' if node.suffix is None else node.suffix.lower()
        signed = 'u' not in suffix
        size = 64 if 'l' in suffix else 32
        node.type = Int(size, signed, True, None, None)
        return node.type

    def variable(self, node: node_type.Variable):
        # variableValidateで見てる
        return node.type

    def assign(self, node: node_type.Assign):
        l_type = self.check(node.left)
        r_type = self.check(node.right)

        # TODO: is_assignable

        node.type = l_type
        return node.type

    def add(self, node: node_type.Add):
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

    def mul(self, node: node_type.Mul):
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
