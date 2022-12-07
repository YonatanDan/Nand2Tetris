package Assembler;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.io.BufferedReader;

public class Parser {
 
    private BufferedReader reader;
    private String currentLine;
    private String currentLineTrim;
    private String nextLine;

    public Parser(File file) throws IOException {
        FileReader fileReader = new FileReader(file);
        this.reader = new BufferedReader(fileReader);

        this.nextLine = null;
        this.currentLine = null;
        this.currentLineTrim = null;
        goToValidLine();
    }

    private void goToValidLine() throws IOException {
        do {
            nextLine = reader.readLine();
        } while (hasMoreLines() && ((nextLine.trim().isEmpty()) 
        || nextLine.trim().startsWith("//"))); 
    }

    public void advance() throws IOException {
        currentLine = nextLine;
        currentLineTrim = currentLine.trim();
        goToValidLine();
    }

    public instructionType instructionType() {
        if (currentLineTrim.startsWith("@")) {
            return instructionType.A_INSTRUCTION;
        } else if (currentLineTrim.startsWith("(")) {
            return instructionType.L_INSTRUCTION;
        } 
        return instructionType.C_INSTRUCTION;
    }

    public String symbol() {
        if (instructionType().equals(instructionType.L_INSTRUCTION)) {
            return currentLineTrim.substring(1, currentLineTrim.indexOf(")"));
        } else if (instructionType().equals(instructionType.A_INSTRUCTION)) {
            return currentLineTrim.substring(1);
        }
        return null;
    }

    public String dest() {
        int endIndex = currentLineTrim.indexOf("=");
        if (endIndex != -1) {
            return currentLineTrim.substring(0, endIndex);
        }
        return null;
    }

    public String comp() {
        int equalIndex = currentLineTrim.indexOf("=");
        int commaIndex = currentLineTrim.indexOf(";");
        String comp = "";
        if (equalIndex != -1) {
            comp = currentLineTrim.replaceAll(" ", "");
            int endIndex = comp.indexOf("//");
            if (endIndex == -1) {
                endIndex = comp.length();
            }
            comp = currentLineTrim.substring(equalIndex + 1, endIndex);
        } else if (commaIndex != -1) {
            comp = currentLineTrim.substring(0, commaIndex);
        }
        return comp;
    }

    public String jump() {
        int startIndex = currentLineTrim.indexOf(";");
        if (startIndex != -1) {         
            String jump = currentLineTrim.replaceAll(" ", "");   
            int endIndex = jump.indexOf("//");
            if (endIndex == -1) {
                endIndex = jump.length();
            }
            return currentLineTrim.substring(startIndex + 1, endIndex);
        }
        return null;
    }

    public boolean hasMoreLines() {
        return (nextLine != null);
    }

    public String addLeadingZeros(String binaryCode) {
        StringBuilder sb = new StringBuilder();
        for (int i = binaryCode.length(); i < 16; i++) {
            sb.append("0");
        }
        sb.append(binaryCode);
        return sb.toString();
    }

    public enum instructionType {
		A_INSTRUCTION,L_INSTRUCTION,C_INSTRUCTION
	}
}
