// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

// This is START
(START)
    // initialize i
    @8192
    D=A
    @i
    M=D

// This is WHILE_TRUE
(WHILE_TRUE)
    // decrement pixel index
    @i
    M=M-1
    D=M
    // if index lt 0, reset it
    @START
    D;JLT
    // if a key is pressed jump to white
    @KBD
    D=M
    @WHITE
    D;JEQ
    // else jump to black
    @BLACK
    0;JMP

// This is WHITE
(WHITE)
    @SCREEN
    D=A
    @i
    A=M+D
    M=0
    @WHILE_TRUE
    0;JMP

// This is BLACK
(BLACK)
    @SCREEN
    D=A
    @i
    A=M+D
    M=-1
    @WHILE_TRUE
    0;JMP
    