from lexer import Lexer
from parser import Parser

# programs = [
#     """
#     Const num=100;
#     Var a1,b2;
#     Begin
#       Read(A1);
#       b2:=a1+num;
#       write(A1,B2);
#     End.
#     """,
#
#     """
#     const a=10;
#     var b,c;
#     begin
#       read(b);
#       c:=a+b;
#       write(c)
#     end.
#     """,
#
#     """
#     var m,n,r,q;
#     const a=10;
#     procedure gcd;
#     begin
#       while r#0 do
#         begin
#           q:=m/n+1;
#           r:=m-q*n;
#           m:=n;
#           n:=r;
#         end
#     end
#
#     begin
#       read(m);
#       read(n);
#
#       if m<n then
#         begin
#           r:=m;
#           m:=n;
#           n:=r;
#         end;
#       if m<=n then ;
#       if m>n then ;
#       if m>=n then ;
#       if odd m then ;
#       begin
#         r:=1;
#         call gcd;
#         write(m);
#       end;
#     end.
#     """
# ]

# programs = [
#     "(a + 15) * b",
#     "a * b + 15"
# ]

# programs = [
#     "var a,d;"
# ]

programs = [
    # 'a := 1 + 2;',
    '''while a#0 DO 
         IF a > b THEN
           begin
             a := c;
             call test;
             write(a+b, fs);
             read(fds, fds);
           end
    '''
]

parser = Parser()

for program in programs:
    tokens = Lexer(program).lex()
    for token in tokens:
        print(token)

    expression = parser.parse_sentence(tokens)
    print(expression)
    print()
