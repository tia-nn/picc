from typing import List, Union, Dict, Tuple, Any

from type import Type
from tokenizer import TK, Token
from utils import debug, warning

from parser.parseutils import Node
from parser.statementparser import *
from parser.exdefinitionparser import ExDefinitionParser


TYPES = 'void', 'char', 'short', 'int', 'long', 'long long', 'float', 'double', '_Bool', '_Complex'
STORAGE_CLASS_SPECIFIER = 'typedef', 'extern', 'static', '_Thread_local', 'auto', 'register'
TYPE_SPECIFIER = 'void', 'char', 'short', 'int', 'long', 'float', 'double', \
                 'signed', 'unsigned', '_Bool', '_Complex'
TYPE_QUALIFIER = 'const', 'restrict', 'volatile', '_Atomic'
FUNCTION_SPECIFIER = 'inline', '_Noreturn'


class Parser(ExDefinitionParser):
    p: int
    nodes: List[Node]
    variables: Dict[str, Type]

    def parse(self, tokens):
        self.p = 0
        nodes = []
        self.variables = {}
        self.offset = {}
        self.tokens = tokens
        #while not self.consume(TK.EOF):
        #    nodes.append(self.translation_unit())
        #return nodes
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
