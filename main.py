from lexer import Lexer
from parser import Parser

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
    const a=10;
    var m,n,r,q;
    procedure gcd;
    begin
      while r#0 do
        begin
          q:=m/n+1;
          r:=m-q*n;
          m:=n;
          n:=r;
        end
    end

    begin
      read(m);
      read(n);

      if m<n then
        begin
          r:=m;
          m:=n;
          n:=r;
        end
      if m<=n then ;
      if m>n then ;
      if m>=n then ;
      if odd m then ;
      begin
        r:=1;
        call gcd;
        write(m);
      end
    end.
    """
]

for program in programs:
    tokens = Lexer(program).lex()
    for token in tokens:
        print(token)

    expression = Parser(tokens).parse_program()
    print(expression)
    print()
