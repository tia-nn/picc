import re
import sys


int_re = re.compile(r'[0-9]+')
ident_re = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*')


def get_int_from_str(s):
    match = int_re.match(s)
    match_str = match.group()
    return match_str


def get_ident_from_str(s):
    match = ident_re.match(s)
    match_str = match.group()
    return match_str


def error(*args):
    sys.stderr.write(' '.join([str(i) for i in args])+'\n')
    exit(1)


def raiser(E):
    def wrap(*args):
        raise E(' '.join([str(i) for i in args])+'\n')
    return wrap


def debug(*args):
    sys.stderr.write('debug: '+(' '.join([str(i) for i in args])+'\n'))



