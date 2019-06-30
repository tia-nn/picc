long f() {
    return 10;
}

long g(long a, long b, long c) {
    printf("%d, %d, %d\n", a, b, c);
    return a + b + c;
}

void print(long a) {
    printf("print: %d\n", a);
}