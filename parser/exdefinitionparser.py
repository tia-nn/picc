from typing import List, Union, Dict, Tuple, Any

from type import Type
from tokenizer import TK, Token
from utils import debug, warning

from parser.parseutils import *
from parser.statementparser import StatementParser


class ExDefinitionParser(StatementParser):

    def translation_unit(self):
        return self.repeat(self.external_declaration)

    def external_declaration(self):
        return self.caller(self.function_definition, self.declaration)

    def function_definition(self):
        decl_specs = self.declaration_specifiers()
        t = self.make_type(decl_specs)
        declarator, pointer = self.declarator()
        if isinstance(declarator, str) or declarator.ty != 'func':
            TypeError('関数宣言には()が必要です')
        name = declarator.name
        parameter_list = declarator.list

        block = self.compound_statement()

        self.variables.set_var(name, Type('.func', func_call_to=t))

        return Node(ND.DEF, val=name, block=block)

