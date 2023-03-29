class VMWriter:

    def __init__(self, output_path):
        self.output_file = open(output_path, 'w')  # Creates new file and prepare it for writing

    def writePush(self, segment, index):
        self.output_file.write('push ' + segment + ' ' + str(index) + '\n') # Writes a VM push command

    def writePop(self, segment, index):
        self.output_file.write('pop ' + segment + ' ' + str(index) + '\n') # Writes a VM pop command

    def writeArithmetic(self, command):
        self.output_file.write(command + '\n') # Writes a VM arithmetic logical command

    def writeLabel(self, label):
        self.output_file.write('label ' + label + '\n') # Writes a VM label command

    def writeGoto(self, label):
        self.output_file.write('goto ' + label + '\n') # Writes a VM goto (label) command

    def writeIf(self, label):
        self.output_file.write('if-goto ' + label + '\n') # Writes a VM if-goto (label) command

    def writeCall(self, name, nArgs):
        self.output_file.write('call ' + name + ' ' + str(nArgs) + '\n') # Writes a VM call command

    def writeFunction(self, name, nVars):
        self.output_file.write('function ' + name + ' ' + str(nVars) + '\n') # Writes a VM function command

    def writeReturn(self):
        self.output_file.write('return\n') # Writes a VM return command

    def close(self):
        self.output_file.close() # Closes the output file