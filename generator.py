from typing import List, Dict, Deque
from collections import deque

from parser.parseutils import Node, ND, Scope
from utils import debug

SIZE_NAME = {
    1: 'BYTE',
    2: 'WORD',
    4: 'DWORD',
    8: 'QWORD',
}
arg_register = 'rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9'
RAX = {1: 'al', 2: 'ax', 4: 'eax', 8: 'rax'}
RDI = {2: 'di', 4: 'edi', 8: 'rdi'}
RSI = {2: 'si', 4: 'esi', 8: 'rsi'}
RDX = {1: 'dl', 2: 'dx', 4: 'edx', 8: 'rdx'}
RCX = {1: 'cl', 2: 'cx', 4: 'ecx', 8: 'rcx'}
R8 = {1: 'r8b', 2: 'r8w', 4: 'r8d', 8: 'r8'}
R9 = {1: 'r9b', 2: 'r9w', 4: 'r9d', 8: 'r9'}
REGISTER = {
    'rax': RAX,
    'rdi': RDI,
    'rsi': RSI,
    'rdx': RDX,
    'rcx': RCX,
    'r8': R8,
    'r9': R9,
}


class Generator:
    scope: Scope
    label_count: int
    now_offset: int
    continue_label: Deque[str]
    break_label: Deque[str]

    def generate(self, nodes: List[Node], vars: Scope):
        self.scope = vars
        self.label_count = 0
        self.now_offset = 0
        self.continue_label = deque()
        self.break_label = deque()
        print('.intel_syntax noprefix')
        print('.global main')
        for node in nodes:
            self.gen(node)

    def gen_addr(self, node: Node):
        if node.ty == ND.IDE:
            if node.type.is_func:
                print('  push OFFSET FLAT :' + node.val)
                return
            _, offset = self.scope.get(node.val)
            print('  mov rax, rbp')
            print('  sub rax,', offset)
            print('  push rax')
            return
        if node.ty == ND.REF:
            self.gen(node.lhs)
            return
        raise TypeError

    def gen(self, node: Node):

        # statement

        if node.ty == ND.DEF:
            print(node.val + ':')
            print('  push rbp')
            print('  mov rbp, rsp')
            self.gen(node.block)
            print('  mov rsp, rbp')
            print('  pop rbp')
            print('  ret')
            return

        if node.ty == ND.LABEL:
            print(f'.L_{node.val}:')
            self.gen(node.block)
            return

        if node.ty == ND.BLOCK:
            # print(node.offset
            self.scope.push_scope(node.scope)
            need_offset = self.scope.max_offset()
            offset = need_offset - self.now_offset
            self.now_offset = offset
            print('  sub rsp,', offset)

            if node.args is not None:
                for i, k in enumerate(node.args):
                    t, o = self.scope.get(k)
                    print('  mov rax, rbp')
                    print('  sub rax,', o)
                    print(f'  mov {SIZE_NAME[t.size]} PTR [rax],', REGISTER[arg_register[i]][t.size])

            for i in node.stmts:
                self.gen(i)

            print('  add rsp,', offset)

            self.scope.pop_scope()
            return

        if node.ty == ND.EXP:
            if node.block is not None:
                self.gen(node.block)
                print('  pop rax')
            return

        l = self.label_count

        if node.ty == 'if':
            self.label_count += 1
            print(f'.LIFS{l}:')
            self.gen(node.condition)
            print('  pop rax')
            print('  cmp rax, 0')
            print(f'  je .LIFE{l}')
            self.gen(node.block)
            print(f'.LIFE{l}:')
            return

        if node.ty == 'if-else':
            self.label_count += 1
            print(f'.LIFS{l}:')
            self.gen(node.condition)
            print('  pop rax')
            print('  cmp rax, 0')
            print(f'  je .LIFEL{l}')
            self.gen(node.block)
            print(f'  jmp .LIFE{l}')
            print(f'.LIFEL{l}:')
            self.gen(node.else_block)
            print(f'.LIFE{l}:')
            return

        if node.ty == 'while':
            self.label_count += 1
            self.continue_label.append(f'.LWHILES{l}')
            self.break_label.append(f'.LWHILEE{l}')
            print(f'.LWHILES{l}:')
            self.gen(node.condition)
            print('  pop rax')
            print('  cmp rax, 0')
            print(f'  je .LWHILEE{l}')
            self.gen(node.block)
            print(f'  jmp .LWHILES{l}')
            print(f'.LWHILEE{l}:')
            self.continue_label.pop()
            self.break_label.pop()
            return

        if node.ty == 'for':
            self.label_count += 1
            self.continue_label.append(f'.LFORS{l}')
            self.break_label.append(f'.LFORE{l}')
            self.scope.push_scope(node.scope)
            need_offset = self.scope.max_offset()
            offset = need_offset - self.now_offset
            self.now_offset = offset
            print('  sub rsp,', offset)

            print(f'.LFORI{l}:')
            if node.init is not None:
                self.gen(node.init)
                if node.init.ty != ND.DECL:
                    print('  pop rax')
            print(f'  jmp .LFORB{l}')
            print(f'.LFORS{l}:')
            if node.proc is not None:
                self.gen(node.proc)
                print('  pop rax')
            print(f'.LFORB{l}:')
            if node.condition is not None:
                self.gen(node.condition)
            else:
                print('push 1')
            print('  pop rax')
            print('  cmp rax, 0')
            print(f'  je .LFORE{l}')
            self.gen(node.block)
            print(f'  jmp .LFORS{l}')
            print(f'.LFORE{l}:')
            print('  add rsp,', offset)

            self.scope.pop_scope()
            self.continue_label.pop()
            self.break_label.pop()
            return

        if node.ty == 'goto':
            print(f'jmp .L_{node.val}')
            return

        if node.ty == 'continue':
            print('jmp', self.continue_label[-1])
            return

        if node.ty == 'break':
            print('jmp', self.break_label[-1])
            return

        if node.ty == 'return':
            self.gen(node.lhs)
            print('  pop rax')
            print('  mov rsp, rbp')
            print('  pop rbp')
            print('  ret')
            return

        if node.ty == ND.DECL:
            for i in node.d_init_list:
                self.gen(i)
            return

        # expression

        if node.ty == ND.INT:
            if node.type.ty in ('int', 'long', 'long long'):  # 整数
                print('  push', node.val)
                return
            raise TypeError

        if node.ty == ND.IDE:
            self.gen_addr(node)
            print('  pop rax')
            if node.type.size < 4:
                if node.type.signed:
                    print(f'  movax rax, {SIZE_NAME[node.type.size]} PTR [rax]')
                else:
                    print(f'  movzx rax, {SIZE_NAME[node.type.size]} PTR [rax]')
            else:
                print(f'  mov {RAX[node.type.size]}, {SIZE_NAME[node.type.size]} PTR [rax]')
            print(f'  push rax')
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

        if node.ty == '++':
            self.gen_addr(node.lhs)
            print('  pop rdi')
            if node.type.size < 4:
                if node.type.signed:
                    print(f'  movax rax, {SIZE_NAME[node.type.size]} PTR [rdi]')
                else:
                    print(f'  movzx rax, {SIZE_NAME[node.type.size]} PTR [rdi]')
            else:
                print(f'  mov {RAX[node.type.size]}, {SIZE_NAME[node.type.size]} PTR [rdi]')
            print('  push rax')
            print('  add rax, 1')
            print(f'  mov {SIZE_NAME[node.type.size]} PTR [rdi], {RAX[node.type.size]}')
            return

        if node.ty == '--':
            self.gen_addr(node.lhs)
            print('  pop rdi')
            if node.type.size < 4:
                if node.type.signed:
                    print(f'  movax rax, {SIZE_NAME[node.type.size]} PTR [rdi]')
                else:
                    print(f'  movzx rax, {SIZE_NAME[node.type.size]} PTR [rdi]')
            else:
                print(f'  mov {RAX[node.type.size]}, {SIZE_NAME[node.type.size]} PTR [rdi]')
            print('  push rax')
            print('  sub rax, 1')
            print(f'  mov {SIZE_NAME[node.type.size]} PTR [rdi], {RAX[node.type.size]}')
            return

        if node.ty == ND.LEA:
            self.gen_addr(node.lhs)
            return

        if node.ty == ND.REF:
            self.gen(node.lhs)
            print('  pop rax')
            if node.lhs.type.size < 4:
                if node.type.signed:
                    print(f'  movax rax, {SIZE_NAME[node.lhs.type.size]} PTR [rax]')
                else:
                    print(f'  movzx rax, {SIZE_NAME[node.lhs.type.size]} PTR [rax]')
            else:
                print(f'  mov {RAX[node.type.size]}, {SIZE_NAME[node.type.size]} PTR [rax]')
            print(f'  push rax')
            return

        if node.ty == '=':
            self.gen_addr(node.lhs)
            self.gen(node.rhs)
            print('  pop rdi')
            print('  pop rax')
            print(f'  mov {SIZE_NAME[node.lhs.type.size]} PTR [rax], {RDI[node.lhs.type.size]}')  # todo: 右のレジスタのサイズを調整
            print('  push rdi')
            return

        if node.ty == ',':
            self.gen(node.lhs)
            print('pop rax')
            self.gen(node.rhs)
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
