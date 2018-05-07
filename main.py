from lexer import Lexer
from parser import Parser
from generator import IRGenerator

programs = [
    """
    Const num=100;
    Var a1,b2;
    Begin
      Read(A1);
      b2:=a1+num;
      write(A1,B2);
    End.
    """,

    """
    const a=10;
    var b,c;
    begin
      read(b);
      c:=a+b;
      write(c);
    end.
    """,

    """
    VAR x, squ;

    PROCEDURE square;
    BEGIN
        squ:= x * x;
    END

    BEGIN
        x := 1;
        WHILE x <= 10 DO
        BEGIN
            CALL square;
            WRITE(squ);
            x := x + 1;
        END
    END.
    """,
    """
    const max = 100;
    var arg, ret;

    procedure isprime;
    var i;
    begin
        ret := 1;
        i := 2;
        while i < arg do
        begin
            if arg / i * i = arg then
            begin
                ret := 0;
                i := arg;
            end
            i := i + 1;
        end
    end

    procedure primes;
    begin
        arg := 2;
        while arg < max do
        begin
            call isprime;
            if ret = 1 then write(arg);
            arg := arg + 1;
        end
    end

    call primes;
    .
    """,
    """
    VAR x, y, z, q, r, n, f;

    PROCEDURE multiply;
    VAR a, b;
    BEGIN
        a := x;
        b := Y;
        z := 0;
        WHILE b > 0 DO
        BEGIN
            IF ODD(b) THEN z := z + a;
            a := 2 * a;
            b := b / 2;
        END
    END

    PROCEDURE divide;
    VAR w;
    BEGIN
        r := x;
        q := 0;
        w := y;
        WHILE w <= r DO w := 2 * w;
        WHILE w > y DO
        BEGIN
            q := 2 * q;
            w := w / 2;
            IF w <= r THEN
            BEGIN
                r := r - w;
                q := q + 1;
            END
        END
    END

    PROCEDURE gcd;
    VAR f, g;
    BEGIN
        f := x;
        g := y;
        WHILE f # g DO
        BEGIN
            IF f < g THEN g := g - f;
            IF g < f THEN f := f - g;
        END
        z := f;
    END

    PROCEDURE fact;
    BEGIN
        IF n > 1 THEN
        BEGIN
            f := n * f;
            n := n - 1;
            CALL fact;
        END
    END

    BEGIN
        read(x); read(y); CALL multiply; write(z);
        read(x); read(y); CALL divide; write(q); write(r);
        read(x); read(y); CALL gcd; write(z);
        read(n); f := 1; CALL fact; write(f);
    END.
    """
]

for program in programs:
    tokens = Lexer(program).lex()
    for token in tokens:
        print(token)

    program = Parser(tokens).parse_program()
    print(program)

    generator = IRGenerator(program.content.content)
    generator.emit()
    print(generator.module)
    generator.generate()
    generator.run()
    print()
