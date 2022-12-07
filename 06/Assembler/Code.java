package Assembler;
import java.util.HashMap;

public class Code {

    private HashMap<String, String> destDict;
    private HashMap<String, String> compDict;
    private HashMap<String, String> jumpDict;

    public Code() {
        this.destDict = new HashMap<String, String>();
        this.compDict = new HashMap<String, String>();
        this.jumpDict = new HashMap<String, String>();

        initDest();
        initComp();
        initJump();
    }

    private void initDest() {
        destDict.put(null, "000");
        destDict.put("M", "001");
        destDict.put("D", "010");
        destDict.put("DM", "011");
        destDict.put("MD", "011");
        destDict.put("A", "100");
        destDict.put("AM", "101");
        destDict.put("AD", "110");
        destDict.put("ADM", "111");
    }

    private void initComp() {
        // a == 0
        compDict.put("0", "0101010");
        compDict.put("1", "0111111");
        compDict.put("-1", "0111010");
        compDict.put("D", "0001100");
        compDict.put("A", "0110000");
        compDict.put("!D", "0001101");
        compDict.put("!A", "0110001");
        compDict.put("-D", "0001111");
        compDict.put("-A", "0110011");
        compDict.put("D+1", "0011111");
        compDict.put("A+1", "0110111");
        compDict.put("D-1", "0001110");
        compDict.put("A-1", "0110010");
        compDict.put("D+A", "0000010");
        compDict.put("D-A", "0010011");
        compDict.put("A-D", "0000111");
        compDict.put("D%A", "0000000");
        compDict.put("D|A", "0010101");
        // a == 1
        compDict.put("M", "1110000");
        compDict.put("!M", "1110001");
        compDict.put("-M", "1110011");
        compDict.put("M+1", "1110111");
        compDict.put("M-1", "1110010");
        compDict.put("D+M", "1000010");
        compDict.put("D-M", "1010011");
        compDict.put("M-D", "1000111");
        compDict.put("D&M", "1000000");
        compDict.put("D|M", "1010101");
    }

    private void initJump() {
        jumpDict.put(null, "000");
        jumpDict.put("JGT", "001");
        jumpDict.put("JEQ", "010");
        jumpDict.put("JGE", "011");
        jumpDict.put("JLT", "100");
        jumpDict.put("JNE", "101");
        jumpDict.put("JLE", "110");
        jumpDict.put("JMP", "111");
    }

    public String dest(String mnemonic) {        
        return destDict.get(mnemonic);
    }

    public String comp(String mnemonic) {
        return compDict.get(mnemonic);
    }

    public String jump(String mnemonic) {
        return jumpDict.get(mnemonic);
    }
}
