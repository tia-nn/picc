from typing import List, Union

import nodor.node as node_type
from nodor.node import Node
import nodor.typor.type as types
from nodor.typor.type import Type


class GenerateError(Exception):
    pass


class Generator:
    def generate(self, node: Node):
        print('section .text')
        print('global _start')
        print('_start:')
        print('call main')
        print('mov rdi, rax')
        print('mov rax, 60')
        print('syscall')
        print('main:')
        self.gen(node)
        print('ret')

    def gen(self, node: Node):
        if isinstance(node, node_type.Integer):
            print(f'mov rax, {node.value & 0xffffffffffffffff}')
            return

        if isinstance(node, node_type.Add):
            self.gen(node.left)
            print('push rax')
            self.gen(node.right)
            print('mov rdi, rax')
            print('pop rax')
            print('add rax, rdi')
            return

        if isinstance(node, node_type.Mul):
            self.gen(node.left)
            print('push rax')
            self.gen(node.right)
            print('mov rdi, rax')
            print('pop rax')
            print('mov edx, 0')
            print('mul rdi')
            return

        raise GenerateError(f'unknown node: {node}')
