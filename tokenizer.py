from typing import List, Union
from enum import Enum, auto
from dataclasses import dataclass
from string import whitespace, digits, ascii_letters, hexdigits, octdigits

from type import Type


class TokenizeError(Exception):
    pass


class TK(Enum):
    NUM = auto()
    EOF = auto()


@dataclass
class Token:
    ty: Union[TK, str]
    val: Union[int, str]
    type: Type


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

            if code[p] in digits:
                if code[p:p+2] in ('0x', '0X'):
                    """ hex constant """
                    p += 2
                    h = self.get_any(code[p:], hexdigits)
                    d = int(h, 16)
                    p += len(h)
                elif code[p] == '0':
                    """ oct constant """
                    p += 1
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

            print(code[p:])
            raise TokenizeError
        tokens.append(Token(TK.EOF, None, None))
        return tokens


if __name__ == '__main__':
    from sys import argv
    argc = len(argv)

    if argc > 1:
        if argv[1] == 'test':
            t = Tokenizer()
            codes = (
                '123',
                '0123',
                '0x123',
                '123u',
                '123uL',
                '123ULL',
                '123l',
                '123lu',
                '123LLU',
                '123LL',
            )

            for code in codes:
                print(code, '=>', t.tokenize(code))

