from typing import List, Callable, TypeVar
from contextlib import contextmanager
from sys import stdout

import nodor.node as node_type
from nodor.node import Node
from crawler import Crawler

T = TypeVar('T')


@contextmanager
def indent():
    orig_write = stdout.write

    def new_write(s: str):
        orig_write('    ' + s)

    stdout.write = new_write
    yield
    stdout.write = orig_write


def label(fn: T) -> T:
    def wrap(*args, **kwargs):
        print(f'; < {fn.__qualname__.split(".")[-1]} >')
        with indent():
            ret = fn(*args, *kwargs)
        return ret
    return wrap


class GenerateError(Exception):
    pass


class Generator(Crawler):

    def generate(self, nodes: List[Node]):
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
    def gen_addr(self, node: node_type.Variable):
        print(f'lea rax, [rbp - {node.offset}]')
        return

    def gen(self, node: Node):
        return self.check(node)

    @label
    def integer(self, node: node_type.Integer):
        print(f'mov rax, {node.value & 0xffffffffffffffff}')
        return

    @label
    def variable(self, node: node_type.Variable):
        self.gen_addr(node)
        print('mov rdi, rax')
        print('xor eax, eax')
        print(f'mov {node.type.ax()}, [rdi]')
        return

    @label
    def assign(self, node: node_type.Assign):
        self.gen(node.right)
        print('push rax')
        self.gen_addr(node.left)
        print('pop rdi')
        print(f'mov [rax], {node.left.type.di()}')
        print('xor eax, eax')
        print(f'mov {node.left.type.ax()}, {node.left.type.di()}')
        return

    @label
    def add(self, node: node_type.Add):
        self.gen(node.left)
        print('push rax')
        self.gen(node.right)
        print('mov rdi, rax')
        print('pop rax')
        print('add rax, rdi')
        return

    @label
    def mul(self, node: node_type.Mul):
        self.gen(node.left)
        print('push rax')
        self.gen(node.right)
        print('mov rdi, rax')
        print('pop rax')
        print('mov edx, 0')
        print('mul rdi')
        return
