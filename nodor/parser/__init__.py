from typing import List

from ..node import Node
from tokenor import Token, TokenType
from .statement_parser import StatementParser


class Parser(StatementParser):

    def parse(self, tokens: List[Token]) -> List[Node]:
        self.tokens = tokens
        self.p = 0
        nodes = []
        while not self.consume(TokenType.EOF):
            nodes.append(self.expression_statement())
        return nodes
