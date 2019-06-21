import sys

from tokenizer import Tokenizer
from parser import Parser
from generator import Generator


def main(code=None):
    t = Tokenizer()
    p = Parser()
    g = Generator()

    if code is None:
        file_name = sys.argv[1]
        file = open(file_name)
        code = file.read()
        file.close()

    tmp = sys.stdout
    sys.stdout = open('a.s', 'w')

    tokens = t.tokenize(code)
    nodes  = p.parse(tokens)
    g.generate(nodes)

    sys.stdout = tmp

    del tmp


if __name__ == '__main__':

    if len(sys.argv) == 1:
        sys.stderr.write('usage: python picc.py [filename]')
        sys.exit(1)

    if sys.argv[1] == 'test':
        import subprocess
        for case in open('test.picc'):
            code, res = case.split('$')
            res = int(res)
            main(code)
            subprocess.run('gcc -o a a.s'.split())
            a = subprocess.run('./a').returncode
            if a == res:
                print('ok:', code, '=>', a)
            else:
                print('ng:', code, '=>', a)
                print('  should get:', res)
        exit(0)

    main()
