class CodeWriter:

    def __init__(self, file_name):
        self.asm_file = open(file_name, 'w')
        self.if_count = 0 # init comparison counter

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
            clean_name = self.asm_file.name.rsplit('/')[-1].split('.asm')[0] # get the clean .asm file name 
            self.asm_file.write('@' + clean_name + '.' + str(index) + '\n')
        elif segment in ['temp', 'pointer']:
            self.asm_file.write('@R' + str(address_map.get(segment) + int(index)) + '\n')
        else:
            raise Exception("error: illegal memory segment")
            
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