from typing import List, Callable, TypeVar, Generator, Any
from contextlib import contextmanager
from sys import stdout

import nodor.node as node_type
from nodor.node import Node
from crawler import Crawler

T = TypeVar('T')


@contextmanager
def indent() -> Generator[None, None, None]:
    orig_write = stdout.write

    def new_write(s: str) -> None:
        orig_write('    ' + s)

    stdout.write = new_write  # type: ignore  # Cannot assign to a method
    yield
    stdout.write = orig_write  # type: ignore  # Cannot assign to a method


def label(fn: Callable[..., T]) -> Callable[..., T]:
    def wrap(*args: Any, **kwargs: Any) -> T:
        print(f'; < {fn.__qualname__.split(".")[-1]} >')
        with indent():
            ret = fn(*args, *kwargs)
        return ret
    return wrap


class GenerateError(ValueError):
    node: Node

    def __init__(self, node: Node, *args: str):
        super().__init__(*args)
        self.node = node


class CodeGenerator(Crawler[None]):

    def generate(self, nodes: List[Node]) -> None:
        print('section .text')
        print('global _start')
        print('_start:')
        with indent():
            print('call main')
            print('mov rdi, rax')
            print('mov rax, 60')
            print('syscall')
        print('main:')
        with indent():
            print('push rsp')
            print('mov rbp, rsp')
            for i in range(26):
                print(f'mov rax, {i}')
                print('push rax')
            self.crawl(nodes)
            print('leave')
            print('ret')

    @label
    def gen_addr(self, node: node_type.Variable) -> None:
        print(f'lea rax, [rbp - {node.offset}]')
        return

    def gen(self, node: Node) -> None:
        return self.check(node)

    @label
    def integer(self, node: node_type.Integer) -> None:
        print(f'mov rax, {node.value & 0xffffffffffffffff}')
        return

    @label
    def variable(self, node: node_type.Variable) -> None:
        if node.type is None:
            raise GenerateError(node, 'type is None')
        self.gen_addr(node)
        print('mov rdi, rax')
        print('xor eax, eax')
        print(f'mov {node.type.ax()}, [rdi]')
        return

    @label
    def assign(self, node: node_type.Assign) -> None:
        if node.type is None:
            raise GenerateError(node, 'type is None')
        if node.left.type is None:
            raise GenerateError(node.left, 'type is None')
        if node.right.type is None:
            raise GenerateError(node.right, 'type is None')
        self.gen(node.right)
        print('push rax')
        self.gen_addr(node.left)
        print('pop rdi')
        print(f'mov [rax], {node.left.type.di()}')
        print('xor eax, eax')
        print(f'mov {node.left.type.ax()}, {node.left.type.di()}')
        return

    @label
    def add(self, node: node_type.Add) -> None:
        self.gen(node.left)
        print('push rax')
        self.gen(node.right)
        print('mov rdi, rax')
        print('pop rax')
        print('add rax, rdi')
        return

    @label
    def mul(self, node: node_type.Mul) -> None:
        self.gen(node.left)
        print('push rax')
        self.gen(node.right)
        print('mov rdi, rax')
        print('pop rax')
        print('mov edx, 0')
        print('mul rdi')
        return
