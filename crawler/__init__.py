from typing import List, Union, Any, TypeVar, Generic
from abc import ABCMeta, abstractmethod

import nodor.node as node_type
from nodor.node import Node

T = TypeVar('T')


class CrawlError(Exception):
    pass


class Crawler(Generic[T], metaclass=ABCMeta):

    def crawl(self, nodes: List[Node]) -> None:
        for node in nodes:
            self.check(node)

    def check(self, node: Node) -> T:
        if isinstance(node, node_type.Integer):
            return self.integer(node)

        if isinstance(node, node_type.Variable):
            return self.variable(node)

        if isinstance(node, node_type.Assign):
            return self.assign(node)

        if isinstance(node, node_type.Add):
            return self.add(node)

        if isinstance(node, node_type.Mul):
            return self.mul(node)

        raise CrawlError(f'unknown node: {node}')

    @abstractmethod
    def integer(self, node: node_type.Integer) -> T:
        raise NotImplementedError

    @abstractmethod
    def variable(self, node: node_type.Variable) -> T:
        raise NotImplementedError

    @abstractmethod
    def assign(self, node: node_type.Assign) -> T:
        raise NotImplementedError

    @abstractmethod
    def add(self, node: node_type.Add) -> T:
        raise NotImplementedError

    @abstractmethod
    def mul(self, node: node_type.Mul) -> T:
        raise NotImplementedError
