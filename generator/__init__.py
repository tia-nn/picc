from typing import List

import nodor.node as node_type
from nodor.node import Node
from crawler import Crawler


class GenerateError(Exception):
    pass


class Generator(Crawler):

    def generate(self, nodes: List[Node]):
        print('section .text')
        print('global _start')
        print('_start:')
        print('call main')
        print('mov rdi, rax')
        print('mov rax, 60')
        print('syscall')
        print('main:')
        print('push rsp')
        print('mov rbp, rsp')
        for i in range(26):
            print(f'mov rax, {i}')
            print('push rax')
        self.crawl(nodes)
        print('leave')
        print('ret')

    def gen_addr(self, node: node_type.Variable):
        print(f'lea rax, [rbp - {node.offset}]')
        return

    def gen(self, node: Node):
        return self.check(node)

    def integer(self, node: node_type.Integer):
        print(f'mov rax, {node.value & 0xffffffffffffffff}')
        return

    def variable(self, node: node_type.Variable):
        self.gen_addr(node)
        print('mov rax, [rax]')
        return

    def assign(self, node: node_type.Assign):
        self.gen_addr(node.left)
        print('push rax')
        self.gen(node.right)
        print('pop rdi')
        print('mov [rdi], rax')
        return

    def add(self, node: node_type.Add):
        self.gen(node.left)
        print('push rax')
        self.gen(node.right)
        print('mov rdi, rax')
        print('pop rax')
        print('add rax, rdi')
        return

    def mul(self, node: node_type.Mul):
        self.gen(node.left)
        print('push rax')
        self.gen(node.right)
        print('mov rdi, rax')
        print('pop rax')
        print('mov edx, 0')
        print('mul rdi')
        return
