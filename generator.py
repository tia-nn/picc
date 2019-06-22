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

    def gen(self, node: Node):  # TODO: 現状: すべてsigned long型であると仮定

        if node.ty == ND.INT:
            if node.type.ty in ('int', 'long', 'long long'):  # 整数
                print('  push', node.val)
                return

        # 二項演算子

        self.gen(node.lhs)
        self.gen(node.rhs)
        print('  pop rdi')
        print('  pop rax')

        if node.ty == '*':
            print('  imul rdi')

        if node.ty == '/':
            print('  mov rdx, 0')
            print('  idiv rdi')

        if node.ty == '%':
            print('  mov rdx, 0')
            print('  idiv rdi')
            print('  push rdx')
            return

        if node.ty == '+':
            print('  add rax, rdi')

        if node.ty == '-':
            print('  sub rax, rdi')

        if node.ty == '<<':
            print('  mov rcx, rdi')
            print('  sal rax, cl')

        if node.ty == '>>':
            print('  mov rcx, rdi')
            print('  sar rax, cl')

        if node.ty == '<':
            print('  cmp rax, rdi')
            print('  setl al')
            print('  movzx rax, al')

        if node.ty == '<=':
            print('  cmp rax, rdi')
            print('  setle al')
            print('  movzx rax, al')

        if node.ty == '==':
            print('  cmp rax, rdi')
            print('  sete al')
            print('  movzx rax, al')

        if node.ty == '!=':
            print('  cmp rax, rdi')
            print('  setne al')
            print('  movzx rax, al')

        if node.ty == '&':
            print('  and rax, rdi')

        if node.ty == '^':
            print('  xor rax, rdi')

        if node.ty == '|':
            print('  or rax, rdi')

        print('  push rax')
