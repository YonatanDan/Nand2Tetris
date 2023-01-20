class VMWriter:

    def __init__(self, output):
        self.outputFile = open(output, 'w')  #Create new file and prepare it for writing

    def writePush(self, segment, index):
        self.outputFile.write('push ' + segment + ' ' + str(index) + '\n') #Writes a VM push command

    def writePop(self, segment, index):
        self.outputFile.write('pop ' + segment + ' ' + str(index) + '\n') #Writes a VM pop command

    def writeArithmetic(self, command):
        self.outputFile.write(command + '\n') #Writes a VM arithmetic logical command

    def writeLabel(self, label):
        self.outputFile.write('label ' + label + '\n') #Writes a VM label command

    def writeGoto(self, label):
        self.outputFile.write('goto ' + label + '\n') #Writes a VM goto (label) command

    def writeIf(self, label):
        self.outputFile.write('if-goto ' + label + '\n') #Writes a VM if-goto (label) command

    def writeCall(self, name, nArgs):
        self.outputFile.write('call ' + name + ' ' + str(nArgs) + '\n') #Writes a VM call command

    def writeFunction(self, name, nVars):
        self.outputFile.write('function ' + name + ' ' + str(nVars) + '\n') #Writes a VM function command

    def writeReturn(self):
        self.outputFile.write('return\n') #Writes a VM return command

    def close(self):
        self.outputFile.close() #Closes the output file