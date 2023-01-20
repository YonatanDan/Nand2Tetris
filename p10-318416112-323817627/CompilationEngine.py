import JackTokenizer

class CompilationEngine:
    def __init__(self, input_path, output_path):
        self.input_file = JackTokenizer.JackTokenizer(input_path)
        self.output_file = open(output_path, 'w')
        self.current_indent = ""
    
    # compiles a compelete class
    def compile_class(self):
        self.open_non_terminal('class')
        self.write_next_token() # 'class'
        self.write_next_token() # class name
        self.write_next_token() # '{'
        while (self.is_class_var_dec()): # all statics/fields declarations
            self.compile_class_var_dec()
        while self.is_subroutine(): # all subroutines
            self.compile_subroutine()
        self.write_next_token() # '}'
        self.close_non_terminal('class')
        self.output_file.close()
    
    # writes to the output file an opening non terminal statement of type @rule
    def open_non_terminal(self, rule):
        self.output_file.write(self.current_indent + '<' + rule + '>\n')
        self.current_indent += "  " # increment indent
    
    # writes to the output file a closing non terminal statement of type @rule
    def close_non_terminal(self, rule):
        self.current_indent = self.current_indent[:-2] # decrement indent
        self.output_file.write(self.current_indent + '</' + rule + '>\n')
    
    # writes the next token as a terminal statement to the output
    def write_next_token(self):
        token, type = self.input_file.advance()
        if type == 'INT_CONST': type = 'integerConstant' 
        elif type == 'STRING_CONST': type = 'stringConstant'
        else: type = str.lower(type)
        self.output_file.write(self.current_indent + '<{}> {} </{}>\n'.format(type, token, type))

    # returns the next (still unwritten) element in the token list as a tuple
    def get_next_token(self):
        token, type = self.input_file.get_current_element()
        return (token, type)

    # returns true iff the next token is of value @token
    def is_next_token_of_value(self, token):
        return token == self.get_next_token()[0]
    
    # returns true iff the next token is of type @type
    def is_next_token_of_type(self, type):
        return type == self.get_next_token()[1]
    
    ### OTHER HELPER METHODS ###

    def is_class_var_dec(self):
        return self.is_next_token_of_value('static') or self.is_next_token_of_value('field')

    def is_subroutine(self):
        return self.is_next_token_of_value('constructor') or self.is_next_token_of_value('function')\
            or self.is_next_token_of_value('method')
    
    def is_parameter(self):
        return not self.is_next_token_of_type('SYMBOL')
    
    def is_var_dec(self):
        return self.is_next_token_of_value('var')
    
    def is_term(self):
        return self.is_next_token_of_type('INT_CONST') or self.is_next_token_of_type('STRING_CONST')\
            or self.is_next_token_of_type('IDENTIFIER') or self.is_next_token_of_value('(')\
            or (self.get_next_token()[0] in ['-', '~'])\
            or (self.get_next_token()[0] in ['true', 'false', 'null', 'this'])

    def is_statement(self):
        return self.is_next_token_of_value('let')\
            or self.is_next_token_of_value('if')\
            or self.is_next_token_of_value('while')\
            or self.is_next_token_of_value('do')\
            or self.is_next_token_of_value('return')

    # compiles a complete class
    def compile_class_var_dec(self):
        self.open_non_terminal('classVarDec')
        self.write_next_token() # 'static' / 'field'
        self.write_next_token() # variable type
        self.write_next_token() # variable name
        while self.is_next_token_of_value(','):
            self.write_next_token() # ','
            self.write_next_token() # variable name
        self.write_next_token() # ';'
        self.close_non_terminal('classVarDec')
    
    # compiles a complete method, function or constructor
    def compile_subroutine(self):
        self.open_non_terminal('subroutineDec')
        self.write_next_token() # 'constructor'/'method'/'function'
        self.write_next_token() # return type
        self.write_next_token() # name / 'new'
        self.write_next_token() # '('
        self.compile_parameter_list()
        self.write_next_token() # ')'
        self.compile_subroutine_body()
        self.close_non_terminal('subroutineDec')

    # compiles a possibly empty parameter list without the '(' and ')'
    def compile_parameter_list(self): 
        self.open_non_terminal('parameterList')
        while self.is_parameter():
            self.write_next_token() # parameter type
            self.write_next_token() # parameter name
            if self.is_next_token_of_value(','):
                self.write_next_token() # ','
        self.close_non_terminal('parameterList')
    
    # compiles a subroutine's body
    def compile_subroutine_body(self):
        self.open_non_terminal('subroutineBody')
        self.write_next_token() # '{'
        while self.is_var_dec(): # compiles all vars declarations
            self.compile_var_dec()
        self.compile_statements()
        self.write_next_token() # '}'
        self.close_non_terminal('subroutineBody')

    # compile a 'var' declaration
    def compile_var_dec(self):
        self.open_non_terminal('varDec')
        self.write_next_token() # 'var'
        self.write_next_token() # variable type
        self.write_next_token() # variable name
        while self.is_next_token_of_value(','):
            self.write_next_token() # ','
            self.write_next_token() # variable name
        self.write_next_token() # ';'
        self.close_non_terminal('varDec')
    
    # compiles a sequence of statements without the '}' and '{'
    def compile_statements(self):
        self.open_non_terminal('statements')
        while self.is_statement():
            if self.is_next_token_of_value('let'): self.compile_let()
            elif self.is_next_token_of_value('if'): self.compile_if()
            elif self.is_next_token_of_value('while'): self.compile_while()
            elif self.is_next_token_of_value('do'): self.compile_do()
            elif self.is_next_token_of_value('return'): self.compile_return()
        self.close_non_terminal('statements')
    
    # compiles a 'let' statement
    def compile_let(self):
        self.open_non_terminal('letStatement')
        self.write_next_token() # 'let'
        self.write_next_token() # variable name
        if self.is_next_token_of_value('['):
            self.write_next_token() # '['
            self.compile_expression()
            self.write_next_token() # ']'
        self.write_next_token() # '='
        self.compile_expression()
        self.write_next_token() # ';'
        self.close_non_terminal('letStatement')

    # compiles an 'if' statement
    def compile_if(self):
        self.open_non_terminal('ifStatement')
        self.write_next_token() # 'if'
        self.write_next_token() # '('
        self.compile_expression()
        self.write_next_token() # ')'
        self.write_next_token() # '{'
        self.compile_statements() 
        self.write_next_token() # '}'
        if self.is_next_token_of_value('else'):
            self.write_next_token() # 'else'
            self.write_next_token() # '{'
            self.compile_statements()
            self.write_next_token() # '}'
        self.close_non_terminal('ifStatement')

    # compiles a 'while' statement
    def compile_while(self):
        self.open_non_terminal('whileStatement')
        self.write_next_token() # 'while'
        self.write_next_token() # '('
        self.compile_expression()
        self.write_next_token() # ')'
        self.write_next_token() # '{'
        self.compile_statements()
        self.write_next_token() # '}'
        self.close_non_terminal('whileStatement')

    # compiles a 'do' statement
    def compile_do(self):
        self.open_non_terminal('doStatement')
        self.write_next_token() # 'do'
        # call #
        self.write_next_token() # callee name
        if self.is_next_token_of_value('.'):
            self.write_next_token() # '.'
            self.write_next_token() # subroutine name
        self.write_next_token() # '('
        self.compile_expression_list()
        self.write_next_token() # ')'
        # end of call #
        self.write_next_token() # ';'
        self.close_non_terminal('doStatement')

    # compiles a 'return' statement
    def compile_return(self):
        self.open_non_terminal('returnStatement')
        self.write_next_token() # 'return'
        while self.is_term():
            self.compile_expression()
        self.write_next_token() # ';'
        self.close_non_terminal('returnStatement')
    
    # compiles an expression
    def compile_expression(self):
        self.open_non_terminal('expression')
        self.compile_term()
        while self.get_next_token()[0] in ['+', '-', '*', '/', '|', '=', '&lt;', '&gt;', '&amp;']:
            self.write_next_token() # '-'/'~'
            self.compile_term()
        self.close_non_terminal('expression')

    # compiles a term
    def compile_term(self):
        self.open_non_terminal('term')
        if self.is_next_token_of_type('INT_CONST') or self.is_next_token_of_type('STRING_CONST')\
            or (self.get_next_token()[0] in ['true', 'false', 'null', 'this']):
            self.write_next_token() # constant
        elif self.is_next_token_of_type('IDENTIFIER'):
            self.write_next_token() # class/var name
            if self.is_next_token_of_value('['):
                self.write_next_token() # '['
                self.compile_expression()
                self.write_next_token() # ']'
            if self.is_next_token_of_value('('):
                self.write_next_token() # '('
                self.compile_expression_list()
                self.write_next_token() # ')'
            if self.is_next_token_of_value('.'):
                self.write_next_token() # '.'
                self.write_next_token() # subroutine name
                self.write_next_token() # '('
                self.compile_expression_list()
                self.write_next_token() # ')'
        elif self.get_next_token()[0] in ['-', '~']:
            self.write_next_token() # '-'/'~'
            self.compile_term()
        elif self.is_next_token_of_value('('):
            self.write_next_token() # '('
            self.compile_expression()
            self.write_next_token() # ')'
        self.close_non_terminal('term')

    # compiles a possible empty comma seperated list of expressions
    def compile_expression_list(self):
        self.open_non_terminal('expressionList')
        if self.is_term():
            self.compile_expression()
        while self.is_next_token_of_value(','):
            self.write_next_token() # ','
            self.compile_expression()
        self.close_non_terminal('expressionList')
    