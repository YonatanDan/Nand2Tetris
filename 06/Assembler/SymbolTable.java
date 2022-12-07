package Assembler;
import java.util.HashMap;

public class SymbolTable {

    private HashMap<String, Integer> symbolDict;
    
    public SymbolTable() {
        symbolDict = new HashMap<String, Integer>();
        initSymbolTable();
    }

    private void initSymbolTable() {
        symbolDict.put("R0", Integer.valueOf(0));
        symbolDict.put("R1", Integer.valueOf(1));
        symbolDict.put("R2", Integer.valueOf(2));
        symbolDict.put("R3", Integer.valueOf(3));
        symbolDict.put("R4", Integer.valueOf(4));
        symbolDict.put("R5", Integer.valueOf(5));
        symbolDict.put("R6", Integer.valueOf(6));
        symbolDict.put("R7", Integer.valueOf(7));
        symbolDict.put("R8", Integer.valueOf(8));
        symbolDict.put("R9", Integer.valueOf(9));
        symbolDict.put("R10", Integer.valueOf(10));
        symbolDict.put("R11", Integer.valueOf(11));
        symbolDict.put("R12", Integer.valueOf(12));
        symbolDict.put("R13", Integer.valueOf(13));
        symbolDict.put("R14", Integer.valueOf(14));
        symbolDict.put("R15", Integer.valueOf(15));
        symbolDict.put("SCREEN", Integer.valueOf(16384));
        symbolDict.put("KBD", Integer.valueOf(24576));
        symbolDict.put("SP", Integer.valueOf(0));
        symbolDict.put("LCL", Integer.valueOf(1));
        symbolDict.put("ARG", Integer.valueOf(2));
        symbolDict.put("THIS", Integer.valueOf(3));
        symbolDict.put("THAT", Integer.valueOf(4));
    }

    public void addEntry(String symbol, int address) {
        symbolDict.put(symbol, Integer.valueOf(address));
    }

    public boolean contains(String symbol) {
        return symbolDict.containsKey(symbol);
    }

    public int getAddress(String symbol) {
        return symbolDict.get(symbol);
    }
}
