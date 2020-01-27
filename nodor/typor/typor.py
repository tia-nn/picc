from typing import Union, List

from .. import node as node_type
from ..node import Node
from .type import Int


class TypingError(Exception):
    node: Node

    def __init__(self, node: Node, *args):
        super().__init__(args)
        self.node = node


class Typor:

    def typing(self, nodes: List) -> None:
        for node in nodes:
            self.type(node)

    def type(self, node: Node) -> node_type.Type:

        if isinstance(node, node_type.Integer):
            suffix = '' if node.suffix is None else node.suffix.lower()
            signed = 'u' not in suffix
            size = 64 if 'l' in suffix else 32
            node.type = Int(size, signed, True, None, None)
            return node.type

        if isinstance(node, node_type.Add):
            l_type = self.type(node.left)
            r_type = self.type(node.right)

            if isinstance(l_type, Int) and isinstance(r_type, Int):
                signed = l_type.signed or r_type.signed
                size = max(l_type.size, r_type.size)
                node.type = Int(size, signed, True, None, None)
                return node.type

            raise TypingError(node, 'add; unknown leaf\'s type')

        if isinstance(node, node_type.Mul):
            l_type = self.type(node.left)
            r_type = self.type(node.right)

            if isinstance(l_type, Int) and isinstance(r_type, Int):
                signed = l_type.signed or r_type.signed
                size = max(l_type.size, r_type.size)
                node.type = Int(size, signed, True, None, None)
                return node.type

            raise TypingError(node, 'add; unknown leaf\'s type')

        raise TypingError(node, 'unknown node type')

