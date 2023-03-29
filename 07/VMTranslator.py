from Parser import Parser
from CodeWriter import CodeWriter   
import sys

def main(path):
    file_name = path.rsplit('.vm')[0] + '.asm' # extracts the clean file name from the given path
    # constructs the necessery modules for file translation
    code_writer = CodeWriter(file_name)
    parser = Parser(path)
    # iterates through the .vm file, translating it line by line to assembly code
    while parser.has_more_lines():
        parser.advance() # reads the next line
        if parser.command_type() == 'C_PUSH':
            code_writer.write_push_pop('C_PUSH', parser.arg1(), parser.arg2())
        elif parser.command_type() == 'C_POP':
            code_writer.write_push_pop('C_POP', parser.arg1(), parser.arg2())
        elif parser.command_type() == 'C_ARITHMETIC':
            code_writer.write_arithmetic(parser.arg1())

main(sys.argv[1])