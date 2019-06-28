from typing import List, Dict

from parser.parseutils import Node, ND, Scope
from utils import debug


SIZE_NAME = {
    1: 'BYTE',
    2: 'WORD',
    4: 'DWORD',
    8: 'QWORD',
}
arg_register = 'rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9'


class Generator:
    scope: Scope

    def generate(self, nodes: List[Node], vars: Scope):
        self.scope = vars
        print('.intel_syntax noprefix')
        print('.global main')
        for node in nodes:
            self.gen(node)

    def gen_addr(self, node: Node):
        if node.ty == ND.IDE:
            if node.type.is_func:
                print('  push OFFSET FLAT :'+node.val)
                return
            _, offset = self.scope.get(node.val)
            print('  mov rax, rbp')
            print('  sub rax,', offset)
            print('  push rax')
            return
        raise TypeError

    def gen(self, node: Node):

        if node.ty == ND.DEF:
            print(node.val+':')
            print('  push rbp')
            print('  mov rbp, rsp')
            self.gen(node.block)
            print('  mov rsp, rbp')
            print('  pop rbp')
            print('  ret')
            return

        if node.ty == ND.BLOCK:
            # print(node.offset
            self.scope.push_scope(node.scope)
            print('  sub rsp,', self.scope.max_offset())

            if node.args is not None:
                for i, k in enumerate(node.args):
                    _, offset = self.scope.get(k)
                    print('  mov rax, rbp')
                    print('  sub rax,', offset)
                    print('  mov QWORD PTR [rax],', arg_register[i])

            for i in node.stmts:
                self.gen(i)
                print('  pop rax')
            self.scope.pop_scope()
            return

        if node.ty == ND.INT:
            if node.type.ty in ('int', 'long', 'long long'):  # 整数
                print('  push', node.val)
                return
            raise TypeError

        if node.ty == ND.IDE:
            self.gen_addr(node)
            print('  pop rax')
            print(f'  push {SIZE_NAME[node.type.size]} PTR [rax]')
            return

        if node.ty == ND.DECL:
            for i in node.d_init_list:
                self.gen(i)
                print('  pop rax')
            print('  push 0  # decl statement')
            return

        if node.ty == ND.CALL:
            for n in node.call_args[::-1]:
                self.gen(n)
            self.gen_addr(node.call)
            print('  pop rax')
            for i in range(min(len(node.call_args), len(arg_register))):
                print('  pop', arg_register[i])
            print('  call rax')
            print('  push rax')
            return

        if node.ty == '=':
            self.gen_addr(node.lhs)
            self.gen(node.rhs)
            print('  pop rdi')
            print('  pop rax')
            print(f'  mov {SIZE_NAME[node.lhs.type.size]} PTR [rax], rdi')  # todo: 右のレジスタのサイズを調整
            print('  push rdi')
            return

        # 二項演算子

        self.gen(node.lhs)
        self.gen(node.rhs)
        print('  pop rdi')
        print('  pop rax')

        if node.ty == '*':
            if node.rhs.type.signed or node.lhs.type.signed:
                print('  imul rdi')
            else:
                print('  mul rdi')

        if node.ty == '/':
            print('  mov rdx, 0')
            if node.rhs.type.signed or node.lhs.type.signed:
                print('  idiv rdi')
            else:
                print('  div rdi')

        if node.ty == '%':
            print('  mov rdx, 0')
            if node.rhs.type.signed or node.lhs.type.signed:
                print('  idiv rdi')
            else:
                print('  div rdi')
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
            if node.lhs.type.signed:
                print('  sar rax, cl')
            else:
                print('  shr rax, cl')

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
