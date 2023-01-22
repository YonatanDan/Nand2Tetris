import JackTokenizer
import VMWriter
import SymbolTable

class CompilationEngine:
    def __init__(self, input_path, output_path):
        self.tokenizer = JackTokenizer.JackTokenizer(input_path)
        self.vm_writer = VMWriter.VMWriter(output_path)
        self.symbol_table = SymbolTable.SymbolTable()
        self.class_name = ''
        self.subr_name = ''

        self.output_file = open(output_path, 'w')
        self.current_indent = ""
        self.binary_ops_dict = {'+': 'add', '-': 'sub', '*': 'Math.multiply', '/': 'Math.divide', '&amp;': 'and', '|': 'or',
            '=': 'eq', '&lt;': 'lt', '&gt;': 'gt'}
  
    # compiles a compelete class
    def compile_class(self):
        self.pop_next_token()  # 'class' 
        self.class_name = self.pop_next_token()[0]  # class name
        self.pop_next_token()  # '{'
        if self.is_class_var_dec():
            self.compile_class_var_dec()
        while self.is_subroutine():
            self.compile_subroutine()
        self.pop_next_token()  # '}' 
        self.vm_writer.close()
     
    # writes the next token as a terminal statement to the output
    def pop_next_token(self):
        return self.tokenizer.advance()

    # returns the next (still unwritten) element in the token list as a tuple
    def get_next_token(self):
        token, type = self.tokenizer.get_current_element()
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
        while (self.is_class_var_dec()):
            kind = self.pop_next_token()[0] # 'static' / 'field'
            type = self.pop_next_token()[0] # variable type
            name = self.pop_next_token()[0] # variable name
            self.symbol_table.define(name, type, kind)
            while self.is_next_token_of_value(','):
                self.pop_next_token() # ','
                name = self.pop_next_token()[0] # variable name
                self.symbol_table.define(name, type, kind)
            self.pop_next_token() # ';'
    
    # compiles a complete method, function or constructor
    def compile_subroutine(self):
        subr_kind = self.pop_next_token()[0] # 'constructor'/'method'/'function'
        self.pop_next_token() # return type
        self.subr_name = self.class_name + '.' + self.pop_next_token()[0] # name / 'new'
        self.symbol_table.add_subroutine(self.subr_name)
        self.symbol_table.reset()
        self.symbol_table.set_scope(self.subr_name)
        self.pop_next_token() # '('
        self.compile_parameter_list(subr_kind)
        self.pop_next_token() # ')'
        self.compile_subroutine_body(subr_kind)

    # compiles a possibly empty parameter list without the '(' and ')'
    def compile_parameter_list(self, subr_kind):
        if subr_kind == 'method':
            self.symbol_table.define('this', 'self', 'arg')
        while self.is_parameter():
            type = self.pop_next_token()[0] # parameter type
            name = self.pop_next_token()[0] # parameter name
            self.symbol_table.define(name, type, 'arg')
            if self.is_next_token_of_value(','):
                self.pop_next_token() # ','
    
    # compiles a subroutine's body
    def compile_subroutine_body(self, subr_kind):
        self.pop_next_token() # '{'
        while self.is_var_dec(): # compiles all vars declarations
            self.compile_var_dec()
        vars_num = self.symbol_table.var_count('var')
        self.vm_writer.writeFunction(self.subr_name, vars_num)
        if subr_kind == 'method':
            self.vm_writer.writePush('argument', 0)
            self.vm_writer.writePop('pointer', 0)
        elif subr_kind == 'constructor':
            class_vars_num = self.symbol_table.class_count('field')
            self.vm_writer.writePush('constant', class_vars_num)
            self.vm_writer.writeCall('Memory.alloc', 1)
            self.vm_writer.writePop('pointer', 0)         
        self.compile_statements()
        self.pop_next_token() # '}'
        self.symbol_table.set_scope('class')

    # compile a 'var' declaration
    def compile_var_dec(self):
        kind = self.pop_next_token()[0] # 'var'
        type = self.pop_next_token()[0] # variable type
        name = self.pop_next_token()[0] # variable name
        self.symbol_table.define(name, type, kind)
        while self.is_next_token_of_value(','):
            self.pop_next_token() # ','
            name = self.pop_next_token()[0] # variable name
            self.symbol_table.define(name, type, kind)
        self.pop_next_token() # ';'
    
    # compiles a sequence of statements without the '}' and '{'
    def compile_statements(self):
        while self.is_statement():
            if self.is_next_token_of_value('let'): self.compile_let()
            elif self.is_next_token_of_value('if'): self.compile_if()
            elif self.is_next_token_of_value('while'): self.compile_while()
            elif self.is_next_token_of_value('do'): self.compile_do()
            elif self.is_next_token_of_value('return'): self.compile_return()
    
    # compiles a 'let' statement
    def compile_let(self):
        array = False
        self.pop_next_token() # 'let'
        name = self.pop_next_token()[0] # variable name
        if self.is_next_token_of_value('['):
            array = True
            self.pop_next_token() # '['
            self.compile_expression()
            self.pop_next_token() # ']'
            if name in self.symbol_table.current_scope:
                if self.symbol_table.kind_of(name) == 'var':
                    self.vm_writer.writePush('local', self.symbol_table.index_of(name))
                elif self.symbol_table.kind_of(name) == 'arg':
                    self.vm_writer.writePush('argument', self.symbol_table.index_of(name))
            else:
                if self.symbol_table.kind_of(name) == 'static':
                    self.vm_writer.writePush('static', self.symbol_table.index_of(name))
                else:
                    self.vm_writer.writePush('this', self.symbol_table.index_of(name))
            self.vm_writer.writeArithmetic('add')            
        self.pop_next_token() # '='
        self.compile_expression()
        if array:
            self.vm_writer.writePop('temp', 0)
            self.vm_writer.writePop('pointer', 1)
            self.vm_writer.writePop('temp', 0)
            self.vm_writer.writePop('that', 0)
        else: # pop var
            if name in self.symbol_table.current_scope:
                if self.symbol_table.kind_of(name) == 'var':
                    self.vm_writer.writePop('local', self.symbol_table.index_of(name))
                elif self.symbol_table.kind_of(name) == 'arg':
                    self.vm_writer.writePop('argument', self.symbol_table.index_of(name))
            else:
                if self.symbol_table.kind_of(name) == 'static':
                    self.vm_writer.writePop('static', self.symbol_table.index_of(name))
                else:
                    self.vm_writer.writePop('this', self.symbol_table.index_of(name))        
        self.pop_next_token() # ';'

    # compiles an 'if' statement
    def compile_if(self):
        self.pop_next_token() # 'if'
        self.pop_next_token() # '('
        self.compile_expression()
        self.pop_next_token() # ')'
        if_count = self.symbol_table.counters_dict['if']
        self.symbol_table.counters_dict['if'] += 1
        self.vm_writer.writeIf('IF_' + str(if_count))
        self.vm_writer.writeGoto('ELSE_' + str(if_count))
        self.vm_writer.writeLabel('IF_' + str(if_count))
        self.pop_next_token() # '{'
        self.compile_statements() 
        self.pop_next_token() # '}'
        if self.is_next_token_of_value('else'):
            self.vm_writer.writeGoto('IF_END_' + str(if_count))
            self.vm_writer.writeLabel('ELSE_' + str(if_count))
            self.pop_next_token() # 'else'
            self.pop_next_token() # '{'
            self.compile_statements()
            self.pop_next_token() # '}'
            self.vm_writer.writeLabel('IF_END_' + str(if_count))
        else:
            self.vm_writer.writeLabel('ELSE_' + str(if_count))

    # compiles a 'while' statement
    def compile_while(self):
        while_count = str(self.symbol_table.counters_dict['while'])
        self.symbol_table.counters_dict['while'] += 1
        self.vm_writer.writeLabel('WHILE_START_' + while_count)
        self.pop_next_token() # 'while'
        self.pop_next_token() # '('
        self.compile_expression()
        self.vm_writer.writeArithmetic('not')
        self.vm_writer.writeIf('WHILE_END_' + while_count)
        self.pop_next_token() # ')'
        self.pop_next_token() # '{'
        self.compile_statements()
        self.vm_writer.writeGoto('WHILE_START_' + while_count)
        self.vm_writer.writeLabel('WHILE_END_' + while_count)
        self.pop_next_token() # '}'

    # compiles a 'do' statement
    def compile_do(self):
        self.pop_next_token() # 'do'
        # call #
        caller_name, callee_name, call = '', '', ''
        locals_num = 0
        caller_name = self.pop_next_token()[0]  # class/subroutine/var name
        if self.is_next_token_of_value("."):
            self.pop_next_token()  # '.'
            callee_name = self.pop_next_token()[0]  # subroutine name
            if caller_name in self.symbol_table.current_scope or caller_name in self.symbol_table.class_scope:
                self.direct_push_command(caller_name)
                call = self.symbol_table.type_of(caller_name) + '.' + callee_name
                locals_num += 1
            else:
                call = caller_name + '.' + callee_name
        else:
            self.vm_writer.writePush('pointer', 0)
            locals_num += 1
            call = self.class_name + '.' + caller_name
        self.pop_next_token()  # get '(' symbol
        locals_num += self.compile_expression_list()
        self.vm_writer.writeCall(call, locals_num)
        self.pop_next_token()  # get ')' symbol        
        # end of call #
        self.vm_writer.writePop('temp', 0)
        self.pop_next_token() # ';'
    
    def direct_push_command(self, name):
        if name in self.symbol_table.current_scope:
            if self.symbol_table.kind_of(name) == 'var':
                self.vm_writer.writePush('local', self.symbol_table.index_of(name))
            elif self.symbol_table.kind_of(name) == 'arg':
                self.vm_writer.writePush('argument', self.symbol_table.index_of(name))
        else:
            if self.symbol_table.kind_of(name) == 'static':
                self.vm_writer.writePush('static', self.symbol_table.index_of(name))
            else:
                self.vm_writer.writePush('this', self.symbol_table.index_of(name))

    # compiles a 'return' statement
    def compile_return(self):
        self.pop_next_token() # 'return'
        is_empty = True
        while self.is_term():
            is_empty = False
            self.compile_expression()
        if is_empty:
            self.vm_writer.writePush('constant', 0)
        self.vm_writer.writeReturn()
        self.pop_next_token() # ';'
    
    # compiles an expression
    def compile_expression(self):
        self.compile_term()
        while self.get_next_token()[0] in ['+', '-', '*', '/', '|', '=', '&lt;', '&gt;', '&amp;']:
            binary_op = self.pop_next_token()[0] # binary op
            self.compile_term()
            if binary_op in ['*', '/']:
                self.vm_writer.writeCall(self.binary_ops_dict[binary_op], 2)
            elif binary_op in self.binary_ops_dict:
                self.vm_writer.writeArithmetic(self.binary_ops_dict[binary_op])

    # compiles a term
    def compile_term(self):
        array = False
        # handle constants
        if self.is_next_token_of_type('INT_CONST'):
            int_val = self.pop_next_token()[0] # constant
            self.vm_writer.writePush('constant', int_val)
        elif self.is_next_token_of_type('STRING_CONST'):
            string_val = self.pop_next_token()[0] # constant
            self.vm_writer.writePush('constant', len(string_val))
            self.vm_writer.writeCall('String.new', 1)
            for char in string_val:
                self.vm_writer.writePush('constant', ord(char))
                self.vm_writer.writeCall('String.appendChar', 2)
        elif self.get_next_token()[0] in ['true', 'false', 'null', 'this']:
            keyword = self.pop_next_token()[0]  # constant
            if keyword == "this":
                self.vm_writer.writePush('pointer', 0)
            else:
                self.vm_writer.writePush('constant', 0)
                if keyword == "true":
                    self.vm_writer.writeArithmetic('not')       
        # handle identifiers
        elif self.is_next_token_of_type('IDENTIFIER'):
            locals_num = 0
            name = self.pop_next_token()[0]  # class/var/subr name
            if self.is_next_token_of_value("["):  # if array
                array = True
                self.pop_next_token() # '['
                self.compile_expression()
                self.pop_next_token() # ']'
                if name in self.symbol_table.current_scope:
                    if self.symbol_table.kind_of(name) == 'var':
                        self.vm_writer.writePush('local', self.symbol_table.index_of(name))
                    elif self.symbol_table.kind_of(name) == 'arg':
                        self.vm_writer.writePush('argument', self.symbol_table.index_of(name))
                else:
                    if self.symbol_table.kind_of(name) == 'static':
                        self.vm_writer.writePush('static', self.symbol_table.index_of(name))
                    else:
                        self.vm_writer.writePush('this', self.symbol_table.index_of(name))
                self.vm_writer.writeArithmetic('add')  
            if self.is_next_token_of_value("("):
                locals_num += 1
                self.vm_writer.writePush('pointer', 0)
                self.pop_next_token()  # '('
                locals_num += self.compile_expression_list()
                self.pop_next_token()  # ')' 
                self.vm_writer.writeCall(self.class_name + '.' + name, locals_num)
            elif self.is_next_token_of_value("."):  # call
                self.pop_next_token()  # '.' 
                callee_name = self.pop_next_token()[0]  # subroutine name
                if name in self.symbol_table.current_scope or name in self.symbol_table.class_scope:
                    self.direct_push_command(name)
                    name = self.symbol_table.type_of(name) + '.' + callee_name
                    locals_num += 1            
                else:
                    name = name + '.' + callee_name
                self.pop_next_token()  # '(' 
                locals_num += self.compile_expression_list()
                self.pop_next_token()  # ')'
                self.vm_writer.writeCall(name, locals_num)
            else:
                if array:
                    self.vm_writer.writePop('pointer', 1)
                    self.vm_writer.writePush('that', 0)
                elif name in self.symbol_table.current_scope:
                    if self.symbol_table.kind_of(name) == 'var':
                        self.vm_writer.writePush('local', self.symbol_table.index_of(name))
                    elif self.symbol_table.kind_of(name) == 'arg':
                        self.vm_writer.writePush('argument', self.symbol_table.index_of(name))
                else:
                    if self.symbol_table.kind_of(name) == 'static':
                        self.vm_writer.writePush('static', self.symbol_table.index_of(name))
                    else:
                        self.vm_writer.writePush('this', self.symbol_table.index_of(name))
        # handle unary ops
        elif self.get_next_token()[0] in ['-', '~']:
            unary_op = self.pop_next_token()[0]  # unary op
            self.compile_term()
            if unary_op == '-':
                self.vm_writer.writeArithmetic('neg')
            elif unary_op == '~':
                self.vm_writer.writeArithmetic('not')
        elif self.is_next_token_of_value("("):
            self.pop_next_token()  # '('
            self.compile_expression()
            self.pop_next_token()  # ')'

    # compiles a possible empty comma seperated list of expressions
    def compile_expression_list(self):
        expression_count = 0
        if self.is_term():
            self.compile_expression()
            expression_count += 1
        while self.is_next_token_of_value(','):
            self.pop_next_token() # ','
            self.compile_expression()
            expression_count += 1
        return expression_count
    