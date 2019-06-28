from typing import List, Union, Dict, Tuple, Any

from type import Type
from tokenizer import TK, Token
from utils import debug, warning

from parser.parseutils import Node, Scope
from parser.statementparser import *
from parser.exdefinitionparser import ExDefinitionParser


class Parser(ExDefinitionParser):

    def parse(self, tokens):
        self.p = 0
        self.variables = Scope()
        self.tokens = tokens
        return self.translation_unit()


if __name__ == '__main__':
    from sys import argv
    from tokenizer import Tokenizer

    argc = len(argv)

    if argc > 1:
        if argv[1] == 'test':
            t = Tokenizer()
            tokens = t.tokenize('3u * -7')
            print(tokens)
            p = Parser()
            nodes = p.parse(tokens)
            print(nodes)
