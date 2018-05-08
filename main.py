from argparse import ArgumentParser
from subprocess import run
from pathlib import Path
from lexer import Lexer
from parser import Parser
from compiler import Compiler


argparser = ArgumentParser(description='Compile PL0 source.')
argparser.add_argument('source_file', nargs=1, metavar='file', type=str, help='source file of PL0 program')
argparser.add_argument('-o', nargs=1, metavar='file', type=str, help='output file of PL0 program')
argparser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

args = argparser.parse_args()
verbose = args.verbose
source_file = args.source_file[0]
filename = Path(source_file).name.split('.')[0]
bit_code_file = filename + '.bc'
object_file = filename + '.o'
out_files = args.o
if out_files is None:
    out_file = filename
else:
    out_file = out_files[0]

source_f = open(source_file, 'r')
source = source_f.read()
source_f.close()

tokens = Lexer(source).lex()

if verbose:
    print('Tokens:')
    for token in tokens:
        print(token)
    print()

program = Parser(tokens).parse_program()

if verbose:
    print(program)
    print()

compiler = Compiler(program.content.content)
ir_source = compiler.compile()

if verbose:
    print(ir_source)
    print()

bit_code_f = open(bit_code_file, 'w')
bit_code_f.write(ir_source)
bit_code_f.close()

run(['/usr/local/opt/llvm/bin/llc', '-filetype=obj', bit_code_file, '-o', object_file])
run(['gcc', object_file, '-o', out_file])
