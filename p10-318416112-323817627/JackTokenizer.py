import re

KEYWORDS = {"class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean",
                     "void", "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"}
SYMBOLS = {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '<', '>', '=', '~'}

class JackTokenizer:

    def __init__(self, file_path):
        self.file = open(file_path)
        self.text = self.file.read()
        self.clean_file()
        self.current_token = None
        self.token_list = self.tokenize()

    # removes all comments from file
    def clean_file(self):
        final_text = ''
        i = 0
        while i < len(self.text):
            current_char = self.text[i]
            if current_char == '\"': # reached start of string
                end_of_string = self.text.find("\"", i + 1)
                final_text += self.text[i:end_of_string+1] # appends the entire string to the final text
                i = end_of_string + 1
            elif current_char == '/': # maybe reached start of comment
                if self.text[i+1] == '/': # if comment type is "//"
                    end_of_comment = self.text.find('\n', i + 1)  # skips the entire comment
                    i = end_of_comment + 1
                elif self.text[i+1] == '*': # if comment type is "/*"
                    end_of_comment = self.text.find('*/', i + 1)
                    i = end_of_comment + 2
                else: # not a comment (just a '/')
                    final_text += current_char
                    i += 1
            else: 
                final_text += current_char
                i += 1
        self.text = final_text
    
    # returns a list of every token in the .jack file by order
    def tokenize(self):
        # define regex for every token type
        keyword_regex = '(?!\w)|'.join(KEYWORDS) + '(?!\w)'
        symbol_regex = '[' + re.escape('|'.join(SYMBOLS)) + ']'
        int_const_regex = r'\d+'
        string_const_regex = r'"[^"\n]*"'
        identifiers_regex = r'[\w]+'
        global_regex = re.compile(keyword_regex + '|' + symbol_regex + '|' + int_const_regex 
        + '|' + string_const_regex + '|' + identifiers_regex)

        tokens_list = [] # list of tuples of the form - (token, token_type)
        for match in re.findall(global_regex, self.text):
            if re.match(keyword_regex, match) != None:
                tokens_list.append((match, "KEYWORD"))
            elif re.match(symbol_regex, match) != None:
                if match == '<': match = '&lt;'
                elif match == '>': match = '&gt;'
                elif match == '"': match = '&quot;'
                elif match == '&': match = '&amp;'
                tokens_list.append((match, "SYMBOL"))
            elif re.match(int_const_regex, match) != None:
                tokens_list.append((match, "INT_CONST"))
            elif re.match(string_const_regex, match) != None:
                tokens_list.append((match[1:-1], "STRING_CONST"))
            else: 
                tokens_list.append((match, "IDENTIFIER"))
        return tokens_list
    
    # return true iff there are more tokens in the input
    def has_more_tokens(self):
        return self.token_list != []

    # gets the next token from the input and makes it the current token and returns it
    def advance(self):
        if self.has_more_tokens():
            self.current_token = self.token_list.pop(0)
            return self.current_token

    # return the next element in the token list, i.e the head of the token list
    def get_current_element(self):
        if self.has_more_tokens():
            return self.token_list[0]

    # returns the type of the current token
    def token_type(self):
        return self.current_token[1]

    # returns the keyword which is the current token
    def keyword(self):
        if self.token_type() == "KEYWORD":
            return str.upper(self.current_token[0])

    # returns the character which is the current token 
    def symbol(self):
        if self.token_type() == "SYMBOL":
            return self.current_token[0]

    # returns the string which is the current token
    def identifier(self):
        if self.token_type() == "IDENTIFIER":
            return self.current_token[0]

    # returns the integer value which is the current token
    def int_val(self):
        if self.token_type() == "INT_CONST":
            return int(self.current_token[0])

    # returns the string value of the current token without the opening/closing double quotes
    def string_val(self):
        if self.token_type() == "STRING_CONST":
            return self.current_token[0]
