from typing import List, Union, Any, Optional
from enum import Enum, auto
from dataclasses import dataclass
from string import whitespace, digits, hexdigits, ascii_letters, ascii_lowercase
import re

number_literal_chars = set(digits + ascii_letters + '.')
ident_first_chars = set(ascii_letters + '_')
ident_chars = set(ascii_letters + '_' + digits)

token_single = '+*;=()'
alphabet_token = ['do',
                  'if',
                  'int',
                  'for',
                  'void',
                  'enum',
                  'char',
                  'else',
                  'auto',
                  'long',
                  'case',
                  'goto',
                  'union',
                  '_Bool',
                  'const',
                  'float',
                  'short',
                  'break',
                  'while',
                  'static',
                  'double',
                  'struct',
                  'sizeof',
                  'extern',
                  'inline',
                  'signed',
                  'switch',
                  'return',
                  'default',
                  'typedef',
                  '_Atomic',
                  '_Alignof',
                  'register',
                  '_Generic',
                  'unsigned',
                  '_Alignas',
                  'continue',
                  'restrict',
                  '_Complex',
                  'volatile',
                  '_Noreturn',
                  '_Imaginary',
                  '_Thread_local',
                  '_Static_assert']

alphabet_token_re = [re.compile(i + r'([^a-zA-Z0-9_]|$)') for i in alphabet_token]


class TokenType(Enum):
    NUMBER = auto()
    IDENT = auto()
    EOF = auto()


@dataclass
class Token:
    type: Union[str, TokenType]
    position: int
    value: Any = None

    def __bool__(self) -> bool:
        try:
            self.type
            return True
        except AttributeError:
            return False


class TokenizeError(Exception):
    position: Optional[int] = None
    info: Optional[str] = None

    def __init__(self, position: int, *args: str) -> None:
        super().__init__(args)
        self.position = position


class Tokenizer:

    @staticmethod
    def tokenize(code: str) -> List[Token]:
        p = 0
        code_len = len(code)
        tokens: List[Token] = []

        while p < code_len:
            c = code[p]

            if c in whitespace:
                p += 1
                continue

            if c in token_single:
                tokens.append(Token(c, p))
                p += 1
                continue

            if c in digits:
                num = ''
                first_p = p
                while p < code_len and (c := code[p]) in number_literal_chars:
                    num += c
                    p += 1
                tokens.append(Token(TokenType.NUMBER, first_p, num))
                continue

            if c in ident_first_chars:
                for i, r in enumerate(alphabet_token_re):
                    if r.match(code[p:]):
                        tokens.append(Token(alphabet_token[i], p))
                        p += len(alphabet_token[i])
                        break
                else:
                    ide = ''
                    first_p = p
                    while p < code_len and (c := code[p]) in ident_chars:
                        ide += c
                        p += 1
                    tokens.append(Token(TokenType.IDENT, first_p, ide))
                continue

            raise TokenizeError(p, f'unknown token char: {c}')

        tokens.append(Token(TokenType.EOF, p))
        return tokens
