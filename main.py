from nodor.parse import Nodor
from tokenor.tokenor import Tokenizer
from nodor.typor import typor

if __name__ == '__main__':
    while True:
        node = Nodor().parse(Tokenizer.tokenize(input()))
        typor.Typor().type(node)
        print(node)
