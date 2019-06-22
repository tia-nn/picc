from typing import List, Union
from enum import Enum, auto
from dataclasses import dataclass
from string import whitespace, digits, ascii_letters, hexdigits, octdigits
import sys

from type import Type


AL_ = ascii_letters + '_'
ALNUM_ = AL_ + digits

ALNUM_TOKENS = (
    'do', 'if',
    'for', 'int',
    'auto', 'case', 'char', 'else', 'enum', 'goto', 'long', 'void',
    'break', 'const', 'float', 'short', 'union', 'while',
    'double', 'extern', 'return', 'signed', 'sizeof', 'static', 'struct', 'switch',
    'default', 'typedef',
    'continue', 'register', 'unsigned', 'volatile'
)

SYM_TOKENS = (
    *('==', '!=', '<=', '>=', '++', '--', '<<', '>>', ),
    *'+-*/()=<>;{},&[]%:^|',
)

TOKENS = ALNUM_TOKENS+SYM_TOKENS


class TokenizeError(Exception):
    pass


class TK(Enum):
    NUM = auto()
    IDE = auto()
    EOF = auto()


@dataclass
class Token:
    ty: Union[TK, str]
    val: Union[int, str] = None
    type: Type = None


class Tokenizer:
    def get_any(self, s, any):
        ret = ''
        ls = len(s)
        p = 0
        while p < ls:
            if s[p] in any:
                ret += s[p]
                p += 1
            else:
                break
        return ret

    def tokenize(self, code):
        p = 0
        cl = len(code)
        code += ' ' * 10  # indexError防止
        tokens = []

        while p < cl:
            if code[p] in whitespace:
                p += 1
                continue

            if code[p:p+2] == '//':
                p += 2
                while True:
                    if code[p:p+2] == '\\\n':
                        p += 2
                        continue
                    if code[p] != '\n':
                        break
                    p += 1
                p += 1
                continue

            if code[p:p+2] == '/*':
                p += 2
                while code[p:p+2] != '*/':
                    p += 1
                p += 2
                continue

            f = False
            for token in TOKENS:
                t_len = len(token)
                if code[p:p + t_len] == token and (token[-1] not in ALNUM_ or code[p+t_len] not in ALNUM_):
                    tokens.append(Token(token))
                    p += t_len
                    f = True
                    break
            if f:
                continue

            # 定数式
            if code[p] in digits:
                if code[p:p+2] in ('0x', '0X'):
                    """ hex constant """
                    p += 2
                    h = self.get_any(code[p:], hexdigits)
                    d = int(h, 16)
                    p += len(h)
                elif code[p] == '0':
                    """ oct constant """
                    o = self.get_any(code[p:], octdigits)
                    d = int(o, 8)
                    p += len(o)
                else:
                    """ dec constant """
                    ds = self.get_any(code[p:], digits)
                    d = int(ds)
                    p += len(ds)

                u = False
                l = False
                ll = False

                if code[p:p+2] in ('ll', 'LL'):
                    p += 2
                    ll = True
                    if code[p] in 'uU':
                        p += 1
                        u = True

                elif code[p] in 'lL':
                    p += 1
                    l = True
                    if code[p] in 'uU':
                        p += 1
                        u = True

                if code[p] in 'uU':
                    p += 1
                    u = True
                    if code[p:p+2] in ('ll', 'LL'):
                        p += 2
                        ll = True
                    if code[p] in 'lL':
                        p += 1
                        l = True

                ts = 'long long' if ll else 'long' if l else 'int'
                t = Type(ts, signed=not u)
                tokens.append(Token(TK.NUM, val=d, type=t))
                continue

            if code[p] in AL_:  # todo: http://port70.net/~nsz/c/c11/n1570.html#6.4.3
                t = self.get_any(code[p:], ascii_letters+digits+'_')
                tokens.append(Token(TK.IDE, val=t))
                p += len(t)
                continue

            sys.stderr.write(code[p:]+'\n')
            raise TokenizeError
        tokens.append(Token(TK.EOF))
        return tokens


if __name__ == '__main__':
    from sys import argv
    argc = len(argv)

    if argc > 1:
        if argv[1] == 'test':
            t = Tokenizer()
            codes = (
                '++aa',
            )

            for code in codes:
                print(code, '=>', t.tokenize(code))

