import os
import sys
from CompilationEngine import CompilationEngine

def main():
    dir_path = sys.argv[1]
    if os.path.isdir(dir_path): # if path is a directory
        if not dir_path.endswith('/'):
            dir_path += '/'
        file_list = os.listdir(dir_path)
        for file_name in file_list: # iterates through each file and generates the .xml file 
            if file_name.endswith('.jack'):
                raw_name = file_name.split('.')[0]
                compilation_engine = CompilationEngine(dir_path + file_name, dir_path + raw_name + '.vm')
                compilation_engine.compile_class()
    elif os.path.isfile(dir_path): # if path is a file
        dir_path = dir_path.split('.')[0]
        compilation_engine = CompilationEngine(dir_path + '.jack', dir_path + '.vm')
        compilation_engine.compile_class()
    else:
        raise Exception('illegal argument exception: input must be a valid file/directory path')

main()