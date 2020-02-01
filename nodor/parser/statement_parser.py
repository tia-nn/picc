from typing import List, Union, Callable, Optional, Tuple
import re

from tokenor import Token, TokenType, Tokenizer
from .base import BaseParser, TokenParser, Unmatch, ParseError, unmatch_is_error
from ..node import *
from .expression_parser import ExpressionParser


class StatementParser(ExpressionParser):

    def expression_statement(self) -> Statement:
        result = self.expression()
        if not self.consume(';'):
            raise ParseError(self.p, 'expression statement: no ";"')
        return result

