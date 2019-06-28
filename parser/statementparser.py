from typing import List, Union, Dict, Tuple, Any

from type import Type
from tokenizer import TK, Token
from utils import debug, warning

from parser.parseutils import *
from parser.declarationparser import DeclarationParser
from parser.tokenparser import TK


class StatementParser(DeclarationParser):
    def statement(self):
        return self.caller(
            self.compound_statement,
            self.expression_statement,
            self.selection_statement,
            self.iteration_statement,
            self.jump_statement,
        )

    def compound_statement(self, made_new_scope=False):
        if self.consume('{'):
            if not made_new_scope:
                self.variables.new_scope()
            stmt = self.repeat(self.block_item)
            self.consume_must('}')
            return Node(ND.BLOCK, stmts=stmt, scope=self.variables.pop_scope())

        raise ParseError

    def block_item(self):
        return self.caller(self.declaration, self.statement)

    def expression_statement(self):
        exp = self.select(self.expression)
        try:
            self.consume_must(';')
        except TypeError:
            raise ParseError

        return Node(ND.EXP, block=exp)

    def selection_statement(self):
        if self.consume('if'):
            self.consume_must('(')
            condition = self.expression()
            self.consume_must(')')
            stmt = self.statement()
            if self.consume('else'):
                stmt2 = self.statement()
                return Node('if-else', condition=condition, block=stmt, else_block=stmt2)
            return Node('if', condition=condition, block=stmt)

        raise ParseError

    def iteration_statement(self):
        if self.consume('while'):
            self.consume_must('(')
            condition = self.expression()
            self.consume_must(')')
            stmt = self.statement()
            return Node('while', condition=condition, block=stmt)

        if self.consume('for'):
            self.variables.new_scope()
            self.consume_must('(')
            try:
                init = self.declaration()
            except ParseError:
                init = self.select(self.expression)
                self.consume_must(';')
            condition = self.select(self.expression)
            self.consume_must(';')
            proc = self.select(self.expression)
            self.consume_must(')')
            stmt = self.statement()
            return Node('for', init=init, condition=condition, proc=proc, block=stmt, scope=self.variables.pop_scope())

        raise ParseError

    def jump_statement(self):
        if self.consume('goto'):
            ide = self.consume_must(TK.IDE).val
            self.consume_must(';')
            return Node('goto', val=ide)

        if self.consume('continue'):
            self.consume_must(';')
            return Node('continue')

        if self.consume('break'):
            self.consume_must(';')
            return Node('break')

        if self.consume('return'):
            exp = self.select(self.expression)
            self.consume_must(';')
            return Node('return', lhs=exp)

        raise ParseError
