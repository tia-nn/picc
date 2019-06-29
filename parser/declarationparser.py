from typing import List, Union, Dict, Tuple, Any, Optional
from type import Type
from tokenizer import TK, Token
from utils import debug, warning
from copy import copy

from parser.parseutils import *
from parser.expressionparser import ExpressionParser


class DeclarationParser(ExpressionParser):
    # declaration

    def declaration(self) -> Node:
        return self.caller(
            self._declaration_1,
            self._declaration_2
        )

    def _declaration_1(self) -> Node:
        declaration_specifiers = self.declaration_specifiers()
        t = self.make_type(declaration_specifiers)
        init_declarator_list = self.select(lambda: self.init_declarator_list(t))
        if init_declarator_list is None:
            init_declarator_list = []
        self.consume_must(';')

        init_list = []
        for name, init in init_declarator_list:
            if init is not None:
                init_list.append(Node('=', type=t, lhs=Node(ND.IDE, type=t, val=name), rhs=init[0]))

        return Node(ND.DECL, type=t, val=init_declarator_list, d_init_list=init_list)

    def _declaration_2(self) -> Node:
        raise ParseError

    def init_declarator_list(self, t):
        init_declarator_list = [self.init_declarator(t)]

        while True:
            if self.consume(','):
                init_declarator_list.append(self.init_declarator(t))
                continue
            break

        return init_declarator_list

    def init_declarator(self, t) -> Tuple[Union[int, str], List[Node]]:
        declarator, pointer = self.declarator()

        if pointer is not None:
            def p(g: InnerNode):
                a = Type('.ptr')

                if g.to is None:
                    a.ptr_to = t
                    return a

                a.ptr_to = p(g.to)
                return a

            t = p(pointer)

        initializer = None
        if self.consume('='):
            if isinstance(declarator, InnerNode):
                raise TypeError('関数が初期化されています')
            initializer = self.initializer()

        # 内部的宣言
        if isinstance(declarator, str):  # スカラ変数
            self.variables.set_var(declarator, t)
        elif isinstance(declarator, InnerNode) and declarator.ty == 'func':
            to = copy(t)
            t = Type('.func')
            t.func_call_to = to
            name = declarator.name
            param_list = declarator.list
            t.param_list = param_list
            self.variables.set_var(name, t)

        if t.const and initializer is None:
            warning('const宣言で初期化されていません')

        return declarator, initializer

    def declarator(self) -> Tuple[Union[str, InnerNode], Optional[InnerNode]]:
        pointer = self.select(self.pointer)
        direct_declarator = self.direct_declarator()
        return direct_declarator, pointer

    def direct_declarator(self) -> Union[str, InnerNode]:
        direct_declarator = None

        try:
            direct_declarator = self.identifier()
        except ParseError:
            pass

        while True:
            if self.consume('('):
                parameter_type_list = self.parameter_type_list()
                direct_declarator = InnerNode('func', list=parameter_type_list, name=direct_declarator)
                self.consume_must(')')
                #continue
            break

        if direct_declarator is None:
            raise ParseError

        return direct_declarator

    def initializer(self) -> List[Node]:
        if self.consume('{'):
            raise TypeError

        initializer = [self.assignment_expression()]

        return initializer

    def pointer(self) -> Optional[InnerNode]:

        pointer = None

        while True:
            if self.consume('*'):
                type_qualifier_list = self.repeat(self.type_qualifier)
                pointer = InnerNode('pointer', type_qualifier_list)
                try:
                    p = self.pointer()
                except ParseError:
                    break
                p.to = pointer
                pointer = p
            break

        if pointer is None:
            raise ParseError

        return pointer

    def parameter_type_list(self) -> List[Tuple[Type, Optional[Union[str, InnerNode]]]]:
        params = self.parameter_list()

        if self.consume(','):
            raise Exception('非対応')

        return params

    def parameter_list(self) -> List[Tuple[Type, Optional[Union[str, InnerNode]]]]:
        return self.sep_repeat(self.parameter_declaration, ',', True)

    def parameter_declaration(self) -> Tuple[Type, Optional[Union[str, InnerNode]]]:
        declaration_specs = self.declaration_specifiers()
        t = self.make_type(declaration_specs)
        try:
            declarator: Optional[Union][str, InnerNode] = self.caller(self.declarator, self.direct_declarator)
        except ParseError:
            declarator = None
        return t, declarator

    """

    def direct_abstract_declarator(self):
        direct_abstract_declarator = None
        if self.consume('('):
            direct_abstract_declarator = self.abstract_declarator()
            self.consume_must(')')

        while True:
            break

        if direct_abstract_declarator is None:
            raise ParseError

        return direct_abstract_declarator

    def initializer(self):
        try:
            return self.assignment_expression()
        except ParseError:
            pass
        if self.consume('{'):
            initializer_list = self.initializer_list()
            self.consume(',')
            self.consume_must('}')
            return initializer_list

        raise ParseError

    def initializer_list(self):
        initializer_list = [self._initializer_list()]

        while True:
            try:
                initializer_list.append(self._initializer_list())
            except ParseError:
                break

        return initializer_list

    def _initializer_list(self):
        try:
            designation = self.designation()
        except ParseError:
            designation = None

        initializer = self.initializer()

        return designation, initializer

    def designation(self):
        designator_list = self.designator_list()
        self.consume_must('=')
        return designator_list

    def designator_list(self):
        designator_list = [self.designator()]

        while True:
            try:
                designator_list.append(self.designator())
            except ParseError:
                break

        return designator_list

    def designator(self):
        if self.consume('['):
            constant_expression = self.constant_expression()
            self.consume_must(']')
            #todo
            return
        if self.consume('.'):
            return self.identifier()
        raise ParseError

    """

    def declaration_specifiers(self) -> List[str]:
        return self.repeat(self.declaration_specifier, False)

    def declaration_specifier(self) -> str:
        return self.caller(
            self.storage_class_specifier,
            self.type_specifier,
            self.type_qualifier,
            self.function_specifier,

        )

    def storage_class_specifier(self) -> str:
        return self.token_consumer(STORAGE_CLASS_SPECIFIER)

    def type_specifier(self) -> str:
        return self.token_consumer(TYPE_SPECIFIER)
        # TODO: atomic, struct, enum, typedef

    def type_qualifier(self) -> str:
        return self.token_consumer(TYPE_QUALIFIER)

    def function_specifier(self) -> str:
        return self.token_consumer(FUNCTION_SPECIFIER)

