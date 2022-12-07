package Assembler;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.BufferedWriter;

public class Assembler {
    public static void main(String[] args) throws IOException {
        // constructs the neccesery modules for file reading and translation
        SymbolTable symbolTable = new SymbolTable();

        File inputFile = new File(args[0]); // searches for the input file
        Parser parser = new Parser(inputFile);

        Code codeTable = new Code();

        // creates the output file
        String outputFileName = args[0].substring(0, args[0].indexOf(".")) + ".hack"; // extracts the actual file name without .asm
        File outputFile = new File(outputFileName);
        // prepares to write to the output file
        FileWriter fileWriter = new FileWriter(outputFile);
        BufferedWriter writer = new BufferedWriter(fileWriter);

        int counter = 0; 

        // first pass
        while (parser.hasMoreLines()) {
            parser.advance(); 
            if (parser.instructionType().equals(Parser.instructionType.L_INSTRUCTION)) {
                symbolTable.addEntry(parser.symbol(), counter);
            } else {
                counter++;
            }  
        }

        parser = new Parser(inputFile); //resets parser
        counter = 16;

        // second pass
        while (parser.hasMoreLines()) {
            parser.advance();
            // handles A instructions
            if (parser.instructionType().equals(Parser.instructionType.A_INSTRUCTION)) {
                String currSymbol = parser.symbol();
                if (Character.isDigit(currSymbol.charAt(0))) {
                    String instToWrite = Integer.toBinaryString(Integer.parseInt(currSymbol));
                    instToWrite = parser.addLeadingZeros(instToWrite);
                    writer.write(instToWrite + "\n");
                } else {
                    if (symbolTable.contains(currSymbol)) {
                        String instToWrite = Integer.toBinaryString(symbolTable.getAddress(currSymbol));
                        instToWrite = parser.addLeadingZeros(instToWrite);
                        writer.write(instToWrite + "\n");
                    } else {
                        symbolTable.addEntry(currSymbol, counter);
                        String instToWrite = Integer.toBinaryString(counter);
                        instToWrite = parser.addLeadingZeros(instToWrite);
                        writer.write(instToWrite + "\n");
                        counter++;
                    }
                }
            // handles C instructions    
            } else if (parser.instructionType().equals(Parser.instructionType.C_INSTRUCTION)) {
                String instToWrite = "111" + codeTable.comp(parser.comp()) 
                + codeTable.dest(parser.dest()) + codeTable.jump(parser.jump());                
                writer.write(instToWrite + "\n");
            }
        }
        writer.close();
    }
}
