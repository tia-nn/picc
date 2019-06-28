from typing import List, Union, Dict, Tuple, Any

from type import Type
from tokenizer import TK, Token
from utils import debug, warning

from parser.parseutils import *
from parser.declarationparser import DeclarationParser


class StatementParser(DeclarationParser):
    def statement(self):
        return self.caller(
            self.expression_statement,
            self.declaration,
        )

    def expression_statement(self):
        p = self.p

        expression = self.expression()
        self.consume_must(';')

        return expression

    def compound_statement(self, made_new_scope=False):
        if self.consume('{'):
            if not made_new_scope:
                self.variables.new_scope()
            stmt = self.repeat(self.statement)
            self.consume_must('}')
            return Node(ND.BLOCK, stmts=stmt, scope=self.variables.pop_scope())

        raise ParseError