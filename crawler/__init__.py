from typing import List, Union
from abc import ABCMeta, abstractmethod

import nodor.node as node_type
from nodor.node import Node


class CrawlError(Exception):
    pass


class Crawler(metaclass=ABCMeta):

    def crawl(self, nodes: List[Node]):
        for node in nodes:
            self.check(node)

    def check(self, node: Node):
        if isinstance(node, node_type.Integer):
            return self.integer(node)

        if isinstance(node, node_type.Variable):
            return self.variable(node)

        if isinstance(node, node_type.Add):
            return self.add(node)

        if isinstance(node, node_type.Mul):
            return self.mul(node)

        raise CrawlError(f'unknown node: {node}')

    @abstractmethod
    def integer(self, node: node_type.Integer):
        raise NotImplementedError

    @abstractmethod
    def variable(self, node: node_type.Variable):
        raise NotImplementedError

    def add(self, node: node_type.Add):
        self.check(node.left)
        self.check(node.right)

    def mul(self, node: node_type.Mul):
        self.check(node.left)
        self.check(node.right)
