from Parser import Parser
from CodeWriter import CodeWriter   
import sys
from os import walk

def main(path):
    code_writer = CodeWriter(get_asm_file_name(path))
    files_to_translate = get_file_list(path, code_writer)
    for file in files_to_translate:
        translate_file(file, code_writer)
    code_writer.close()
    
def translate_file(file_name, code_writer):
    parser = Parser(file_name)
    code_writer.set_file_name(file_name)
    # iterates through the .vm file, translating it line by line to assembly code
    while parser.has_more_lines():
        parser.advance() # reads the next line
        if parser.command_type() == 'C_PUSH':
            code_writer.write_push_pop('C_PUSH', parser.arg1(), parser.arg2())
        elif parser.command_type() == 'C_POP':
            code_writer.write_push_pop('C_POP', parser.arg1(), parser.arg2())
        elif parser.command_type() == 'C_ARITHMETIC':
            code_writer.write_arithmetic(parser.arg1())
        elif parser.command_type() == 'C_LABEL':
            code_writer.write_label(parser.arg1())
        elif parser.command_type() == 'C_GOTO':
            code_writer.write_goto(parser.arg1())
        elif parser.command_type() == 'C_IF':
            code_writer.write_if(parser.arg1())
        elif parser.command_type() == 'C_FUNCTION':
            code_writer.write_function(parser.arg1(), int(parser.arg2()))
        elif parser.command_type() == 'C_CALL':
            code_writer.write_call(parser.arg1(), int(parser.arg2()))
        elif parser.command_type() == 'C_RETURN':
            code_writer.write_return()    

def get_file_list(path, code_writer):
    if '.vm' in path:
        return [path]
    else:
        code_writer.write_init() # if path is a dir, write bootstrap code to file
        if path[-1] == '/':
            path = path[:-1]
        file_names = next(walk(path), (None, None, []))[2]
        file_list = filter(lambda name: '.vm' in name, file_names)
        return [path + '/' + file for file in file_list]

def get_asm_file_name(path):
    if '.vm' in path:
        file_name = path.rsplit('.vm')[0] + '.asm' # extracts the clean file name from the given path
        return file_name
    else:
        if path[-1] == '/':
            path = path[:-1]
        dirname = path.split('/')[-1]
        file_name = path + '/' + dirname + '.asm'
        return file_name

main(sys.argv[1])