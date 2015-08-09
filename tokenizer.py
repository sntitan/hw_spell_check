import re

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

TOKEN_TYPE = enum('PLUS', 'MINUS', 'STAR', 'DIVIDE', 'MOD', 'EQ', 'NEQ', 'LT',\
                  'LEQ', 'GEQ', 'ASSIGN', 'POINTSTO', 'DOT', 'AND', 'OPENPA', 'CLOSEPA',\
                  'OPENBR', 'CLOSEBR', 'BEGIN', 'END', 'SEMICOLON', 'COMMA', 'ELLIPSIS', 'EOF',\
                  'CINT', 'CCHAR', 'CSTR', \
                  'KW_CHAR', 'KW_SHORT', 'KW_INT', 'KW_VOID', 'KW_STRUCT', 'KW_IF', 'KW_ELSE', 'KW_FOR',\
                  'KW_CONTINUE', 'KW_BREAK', 'KW_RETURN', 'KW_SIZEOF', 'KW_ALIGN', 'KW_CDECL', 'KW_STDCALL',\
                  'TK_INDENT')
#token type
PLUS = 'PLUS' #+
MINUS = 'MINUS' #-
STAR = 'STAR' #*
DIVIDE = 'DIVIDE' #/
MOD = 'MOD' #%
EQ = 'EQ' #==
NEQ = 'NEQ' #!=
LEQ = 'LEQ' #<=
GEQ = 'GEQ' #>=
ASSIGN = 'ASSIGN' #=
POINTSTO = 'POINTSTO' #->
DOT = 'DOT' #.


class Token:
    def __init__(self):
        self.ttype = None
        self.content = None
        self.line_no = 0

#fb: file buffer list, fb[0] means line 1, and so on
#return: 
def token_analysis(fb):
    tokens = []
    space_re =re.compile('^(\s+)')
    number_re = re.compile('^(\d+)')
    keyword_re = re.compile('^((char)|(short)|(int)|(void)|(struct)|(if)|(eles)|(for)|(continue)|(break)|(return)|(sizeof)|(__align)|(__cdecl)|__stdcall)')
    for lno in range(0, len(fb)):
        i = 0
        while(i < len(fb[lno])):
            ma = space_re.match(fb[lno][i:])
            if ma:
                i = i + len(ma.group(0))
                continue
            ma = number_re.match(fb[lno][i:])
            if ma:
                t = Token()
                t.ttype = 'TK_CINT'
                t.content = int(ma.group(0))
                t.line_no = lno + 1
                i = i + lem(ma.group(0))
                continue


