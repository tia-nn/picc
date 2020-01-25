from sys import argv

from nodor.parse import Nodor
from tokenor.tokenor import Tokenizer
from nodor.typor import typor
from generator.generator import Generator


if __name__ == '__main__':
    file_name = 'main.c'
    code = open(file_name).read()
    node = Nodor().parse(Tokenizer.tokenize(code))
    typor.Typor().type(node)
    Generator().generate(node)

    # while True:
    #     node = Nodor().parse(Tokenizer.tokenize(input()))
    #     typor.Typor().type(node)
    #     Generator().generate(node)
