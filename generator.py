from typing import List

from parser import Node, ND


class Generator:
    def generate(self, nodes: List[Node]):
        print('.intel_syntax noprefix')
        print('.global main')
        print('main:')
        for node in nodes:
            self.gen(node)
            print('  pop rax')
        print('  ret')

    def gen(self, node: Node):

        if node.ty == ND.INT:
            if node.type.ty in ('int', 'long', 'long long'):  # 整数
                print('  push', node.val)
                return
