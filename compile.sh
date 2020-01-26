#!/usr/bin/env sh

python main.py > tmp.s
nasm -f elf64 -o tmp.o tmp.s
ld -o tmp tmp.o

cat main.c

./tmp

echo '>>' $?
