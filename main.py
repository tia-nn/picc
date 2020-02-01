from sys import argv, stderr
from typing import List, Tuple

from tokenor import Tokenizer, TokenizeError
from nodor import parse, ErrorReport
from nodor import variable_validator
from nodor.variable_validator.scope import NotExist
from nodor import typor
from generator import Generator, GenerateError


def code_index_to_row_col(code: str, index: int) -> Tuple[int, int]:
    raw: int = 1
    col: int = 1

    for i in range(index):
        c = code[i]
        if c == '\n':
            raw += 1
            col = 0
        else:
            col += 1

    return raw, col


if __name__ == '__main__':
    file_name = 'main.c'
    code = open(file_name).read()
    node = None
    token = None
    try:
        token = Tokenizer.tokenize(code)
    except TokenizeError as e:
        stderr.write(f'{e.position}: {e.args}')
        exit(1)
    # print(token)
    # exit(0)
    try:
        node = parse(token)
    except ErrorReport as e:
        raw, col = code_index_to_row_col(code, e.code_index)
        stderr.write(f'{raw} : {col} : {", ".join(e.args)}')
        exit(1)
    Generator().generate(node)

    # stderr.write(str(node))

    # while True:
    #     node = Nodor().parse(Tokenizer.tokenize(input()))
    #     typor.Typor().type(node)
    #     Generator().generate(node)
