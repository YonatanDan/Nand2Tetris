import re

class Parser:
    
    def __init__(self, file_path):
        self.file = open(file_path, 'r')
        self.final_lines = self.clean_file()
        self.total_lines = len(self.final_lines)

        self.command_index = -1 
        self.current_command = None
        
    # returns the file lines without comments or white space as a list
    def clean_file(self):
        file_lines = self.file.readlines()
        final_lines = []
        for line in file_lines:
            if not (line[:2] == '//') or (line[:2] == '\n'):
                if '//' in line:
                    comment_index = line.find('//') 
                    line = line[:comment_index] # remove the comment from end of line if found
                    line = line.strip()
                final_line = ''
                for c in line:
                    if c not in ['\r', '\n']:
                        final_line += c
                if final_line != '':
                    final_lines.append(final_line)                
            else:
                continue
        return final_lines
    
    # return true iff there are more lines to read in the input
    def has_more_lines(self):
        return self.command_index < self.total_lines - 1
    
    # reads the next command from the input and makes it the current command
    def advance(self):
        if self.has_more_lines():
            self.command_index += 1
            self.current_command = self.final_lines[self.command_index]

    # returns a string representing the type of the current command
    def command_type(self):
        if self.current_command in ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']:
            return 'C_ARITHMETIC'
        elif 'pop' in self.current_command:
            return 'C_POP'
        elif 'push' in self.current_command:
            return 'C_PUSH'
        elif 'label' in self.current_command:
            return 'C_LABEL'
        elif 'if-goto' in self.current_command:
            return 'C_IF'
        elif 'goto' in self.current_command:
            return 'C_GOTO'
        elif 'function' in self.current_command:
            return 'C_FUNCTION'
        elif 'call' in self.current_command:
            return 'C_CALL'
        elif 'return' in self.current_command:
            return 'C_RETURN'
        else:
            raise Exception("error: illegal command")

    # returns the first argument of the current command
    def arg1(self):
        if self.command_type() == 'C_ARITHMETIC':
            return self.current_command
        return self.current_command.split()[1]

    # returns the second argument of the current command
    def arg2(self):
       if self.command_type() in ['C_PUSH', 'C_POP', 'C_FUNCTION', 'C_CALL']:
            return self.current_command.split()[2]