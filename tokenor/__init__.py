from typing import List, Union, Any
from enum import Enum, auto
from dataclasses import dataclass
from string import whitespace, digits, hexdigits, ascii_letters, ascii_lowercase
import re


number_literal_chars = set(digits + ascii_letters + '.')
token_single = '+*;=' + ascii_lowercase


class TokenType(Enum):
    NUMBER = auto()
    EOF = auto()


@dataclass
class Token:
    type: Union[str, TokenType]
    position: int
    value: Any = None

    def __bool__(self):
        try:
            self.type
            return True
        except AttributeError:
            return False


class TokenizeError(Exception):
    position: int = None
    info: str = None

    def __init__(self, position, info):
        super().__init__(self)
        self.position = position
        self.info = info


class Tokenizer:

    @staticmethod
    def tokenize(code) -> List[Token]:
        p = 0
        code_len = len(code)
        tokens = []

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

            raise TokenizeError(p, f'unknown token char: {c}')

        tokens.append(Token(TokenType.EOF, p))
        return tokens
