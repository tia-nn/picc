from typing import Union

from .. import node as node_type
from ..node import Node
from .type import Int


class TypingError(Exception):
    node: Node

    def __init__(self, node: Node, *args):
        super().__init__(args)
        self.node = node


class Typor:

    def type(self, node: Node):
        if isinstance(node, node_type.Integer):
            suffix = '' if node.suffix is None else node.suffix.lower()
            signed = 'u' not in suffix
            size = 64 if 'l' in suffix else 32
            node.type = Int(size, signed, True, None, None)
            return

        raise TypingError(node, 'unknown node type')

