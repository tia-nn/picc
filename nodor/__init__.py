from typing import List

from .parser import Parser
from .parser.base import ParseError, Unmatch
from .node import Node
from tokenor import Token


class ErrorReport(ValueError):
    code_index: int

    def __init__(self, code_index: int, *args):
        super().__init__(*args)
        self.code_index = code_index

    def __str__(self) -> str:
        return f'code index {self.code_index}: {" ".join(self.args)}'


def parse(tokens: List[Token]) -> List[Node]:
    from .variable_validator import VariableValidator, VarNameError
    from .typor import Typor, TypingError
    try:
        nodes = Parser().parse(tokens)
    except ParseError as e:
        raise ErrorReport(tokens[e.position].position, *e.args)
    except Unmatch as e:
        raise ErrorReport(tokens[e.position].position, 'InnerError: ', *e.args)

    try:
        VariableValidator().crawl(nodes)
    except VarNameError as e:
        raise ErrorReport(tokens[e.position].position, *e.args)

    try:
        Typor().typing(nodes)
    except TypingError as e:
        raise ErrorReport(tokens[e.node.position].position, *e.args)

    return nodes
