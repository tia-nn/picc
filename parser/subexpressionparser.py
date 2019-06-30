from parser.parseutils import *
from type import TYPE_SIZE, Type


def max_ty(a, b):
    return max(a, b, key=lambda x: TYPE_SIZE[x])


class SubExpressionParser:
    @staticmethod
    def sub_add(lhs: Node, rhs: Node):
        if lhs.type.is_ptr and rhs.type.is_ptr:
            TypeError('ポインタ同士を加算しようとしています')
        if lhs.type.is_ptr:
            t = lhs.type
            rhs = SubExpressionParser.sub_mul(rhs, Node(ND.INT, type=t_signed_int, val=lhs.type.ptr_to.size))
        elif rhs.type.is_ptr:
            t = rhs.type
            lhs = SubExpressionParser.sub_mul(lhs, Node(ND.INT, type=t_signed_int, val=rhs.type.ptr_to.size))
        else:
            t = Type(max_ty(rhs.type.ty, lhs.type.ty), signed=rhs.type.signed or lhs.type.signed)
        return Node('+', type=t, lhs=lhs, rhs=rhs)

    @staticmethod
    def sub_sub(rhs, lhs):
        a = SubExpressionParser.sub_add(rhs, lhs)
        a.ty = '-'
        return a

    @staticmethod
    def sub_mul(lhs: Node, rhs: Node):
        if not lhs.type.is_arithmetic() or not rhs.type.is_arithmetic():
            raise TypeError('乗算*に算術型以外を指定しています')
        t = Type(max_ty(lhs.type.ty, rhs.type.ty))
        t.signed = lhs.type.signed or rhs.type.signed
        return Node('*', type=t, rhs=rhs, lhs=lhs)

    @staticmethod
    def sub_div(lhs, rhs):
        a = SubExpressionParser.sub_mul(lhs, rhs)
        a.ty = '/'
        return a

    @staticmethod
    def sub_sur(lhs, rhs):
        if not lhs.type.is_integer() and not rhs.type.is_integer():
            TypeError('%に整数型以外をしていしています')
        a = SubExpressionParser.sub_mul(lhs, rhs)
        a.ty = '%'
        return a
