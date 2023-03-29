class CodeWriter:

    def __init__(self, file_name):
        self.asm_file = open(file_name, 'w')
        self.current_read_file = None
        self.if_count = 0 # init comparison counter
        self.call_count = 0 # init call counter

    def write_arithmetic(self, command):
        if command not in ['not', 'neg']: # handles binary commands
            self.pop_stack_to_DReg()
        
        self.decrement_stack() # decrement the stack pointer
        self.set_AReg_to_stack() # and load the value to A register
        # maps every arithmetic vm command to it's matching assembly command
        switcher = {
            'add': 'M=M+D\n',
            'sub': 'M=M-D\n',
            'and': 'M=M&D\n',
            'or': 'M=M|D\n',
            'neg': 'M=-M\n',
            'not': 'M=!M\n',
            'eq': 'D;JEQ\n',
            'gt': 'D;JGT\n',
            'lt': 'D;JLT\n',
        }
        if switcher.__contains__(command):
            # handles comparsion commands
            if command in ['eq', 'gt', 'lt']:
                self.asm_file.write('D=M-D\n')  
                self.asm_file.write('@IF_{count}\n'.format(count = self.if_count))
                self.asm_file.write(switcher.get(command)) # compare DReg to 0
                # if FALSE
                self.set_AReg_to_stack()
                self.asm_file.write('M=0\n')
                self.asm_file.write('@ENDIF_{count}\n'.format(count = self.if_count))
                self.asm_file.write('0;JMP\n')
                # if TRUE
                self.asm_file.write('(IF_{count})\n'.format(count = self.if_count))
                self.set_AReg_to_stack()
                self.asm_file.write('M=-1\n')

                self.asm_file.write('(ENDIF_{count})\n'.format(count = self.if_count))
                self.if_count += 1 # inc if-comparisons counter
            else:
                self.asm_file.write(switcher.get(command))   
        else:
            raise Exception("error: illegal arthimetic command")
        self.increment_stack()
    
    def write_push_pop(self, command, segment, index):
        self.set_AReg_to_seg_address(segment, index) # sets AReg to the correct memory address to push/pop to/from
        # handles push commands
        if command == 'C_PUSH':
            if segment == 'constant':
                self.asm_file.write('D=A\n')
            else:
                self.asm_file.write('D=M\n')
            self.push_DReg_to_stack()
        # handles pop commands
        elif command == 'C_POP':
            self.asm_file.write('D=A\n')
            self.asm_file.write('@R13\n') 
            self.asm_file.write('M=D\n') # store the pop address in R13
            self.pop_stack_to_DReg()
            self.asm_file.write('@R13\n') 
            self.asm_file.write('A=M\n') # gets the pop address back from R13
            self.asm_file.write('M=D\n') # stores the popped value in that address
        else:
            raise Exception("error: illegal push/pop command")

    def set_AReg_to_seg_address(self, segment, index):
        # maps every memory segment to its correct address in memory
        address_map = {
            'local': 'LCL',
            'argument': 'ARG', 
            'this': 'THIS',
            'that': 'THAT',
            'static': 16,
            'temp': 5,
            'pointer': 3,
        }
        # handles each segment group seprately 
        if segment in ['local', 'argument', 'this', 'that']:
            self.asm_file.write('@' + address_map.get(segment) + '\n')
            self.asm_file.write('D=M\n')
            self.asm_file.write('@' + str(index)+ '\n')
            self.asm_file.write('A=D+A\n')
        elif segment == 'constant':
            self.asm_file.write('@' + str(index) + '\n')
        elif segment == 'static': 
            self.asm_file.write('@' + self.current_read_file + '.' + str(index) + '\n')
        elif segment in ['temp', 'pointer']:
            self.asm_file.write('@R' + str(address_map.get(segment) + int(index)) + '\n')
        else:
            raise Exception("error: illegal memory segment")
    
    def write_label(self, label):
        self.asm_file.write('({file}${l})\n'.format(file = self.current_read_file, l = label))

    def write_goto(self, label):
        self.asm_file.write('@{file}${l}\n'.format(file = self.current_read_file, l = label))
        self.asm_file.write('0;JMP\n')
    
    def write_if(self, label):
        self.pop_stack_to_DReg()
        self.asm_file.write('@{file}${l}\n'.format(file = self.current_read_file, l = label))
        self.asm_file.write('D;JNE\n')
    
    def write_function(self, function_name, nVars):
        self.asm_file.write('({fn})\n'.format(fn = function_name))
        for i in range(nVars):
            self.asm_file.write('D=0\n')
            self.push_DReg_to_stack()
    
    def write_call(self, function_name, nArgs):
        # push return address
        return_address = function_name + '$ret.' + str(self.call_count)
        self.call_count += 1
        self.asm_file.write('@' + return_address + '\n')
        self.asm_file.write('D=A\n')
        self.push_DReg_to_stack()
        # push LCL, ARG, THIS, THAT
        for segment in ['LCL', 'ARG', 'THIS', 'THAT']:
            self.asm_file.write('@' + segment + '\n')
            self.asm_file.write('D=M\n')
            self.push_DReg_to_stack()
        # LCL = SP
        self.asm_file.write('@SP\n')
        self.asm_file.write('D=M\n')
        self.asm_file.write('@LCL\n')
        self.asm_file.write('M=D\n')
        # ARG = SP - nArgs - 5
        self.asm_file.write('@SP\n')
        self.asm_file.write('D=M\n')
        self.asm_file.write('@' + str(nArgs + 5) + '\n')
        self.asm_file.write('D=D-A\n')
        self.asm_file.write('@ARG\n')
        self.asm_file.write('M=D\n')
        # goto function_name
        self.asm_file.write('@{fn}\n'.format(fn = function_name))
        self.asm_file.write('0;JMP\n')
        self.asm_file.write('({ret_a})\n'.format(ret_a = return_address))

    def write_return(self):
        # use R13 as endFrame and store LCL
        self.asm_file.write('@LCL\n')
        self.asm_file.write('D=M\n')
        self.asm_file.write('@R13\n')
        self.asm_file.write('M=D\n')
        # store *(endFrame - 5) in retAddress
        self.asm_file.write('@R13\n')
        self.asm_file.write('D=M\n')
        self.asm_file.write('@5\n')
        self.asm_file.write('D=D-A\n')
        self.asm_file.write('A=D\n')
        self.asm_file.write('D=M\n')
        self.asm_file.write('@R14\n') # use R14 as retAddress
        self.asm_file.write('M=D\n')
        # *ARG = pop()
        self.pop_stack_to_DReg()
        self.asm_file.write('@ARG\n')
        self.asm_file.write('A=M\n')
        self.asm_file.write('M=D\n')
        # SP = ARG + 1 
        self.asm_file.write('@ARG\n')
        self.asm_file.write('D=M\n')
        self.asm_file.write('@SP\n')
        self.asm_file.write('M=D+1\n') 
        # THAT = *(endFrame - 1)
        # THIS = *(endFrame - 2)
        # ARG = *(endFrame - 3)
        # LCL = *(endFrame - 4)
        i = 1
        for segment in ['THAT', 'THIS', 'ARG', 'LCL']:
            self.asm_file.write('@R13\n')
            self.asm_file.write('D=M\n')
            self.asm_file.write('@' + str(i) + '\n')
            self.asm_file.write('D=D-A\n')
            self.asm_file.write('A=D\n')
            self.asm_file.write('D=M\n')
            self.asm_file.write('@' + segment + '\n')
            self.asm_file.write('M=D\n')
            i += 1
        # goto retAddress
        self.asm_file.write('@R14\n')
        self.asm_file.write('A=M\n')
        self.asm_file.write('0;JMP\n')
    
    def close(self):
        self.asm_file.close()
    
    def set_file_name(self, file_name):
        self.current_read_file = file_name.split('/')[-1].replace('.vm', '')
        self.asm_file.write('// ' + self.current_read_file + '\n')

    def write_init(self):
        self.asm_file.write('@256\n')
        self.asm_file.write('D=A\n')
        self.asm_file.write('@SP\n')
        self.asm_file.write('M=D\n')
        self.write_call('Sys.init', 0)
        
    ### HELPER FUNCTIONS ###
    def pop_stack_to_DReg(self):
        self.asm_file.write('@SP\n')
        self.asm_file.write('M=M-1\n')
        self.asm_file.write('A=M\n')
        self.asm_file.write('D=M\n')

    def push_DReg_to_stack(self):
        self.asm_file.write('@SP\n')
        self.asm_file.write('A=M\n')
        self.asm_file.write('M=D\n')
        self.asm_file.write('@SP\n')
        self.asm_file.write('M=M+1\n')
        
    def decrement_stack(self):
        self.asm_file.write('@SP\n')
        self.asm_file.write('M=M-1\n')
    
    def increment_stack(self):
        self.asm_file.write('@SP\n')
        self.asm_file.write('M=M+1\n')

    def set_AReg_to_stack(self):
        self.asm_file.write('@SP\n')
        self.asm_file.write('A=M\n')