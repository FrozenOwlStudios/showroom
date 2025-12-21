grammar SimpleLangGrammar;

//==============================================================================
//                                  PARSER
//==============================================================================

program
    :statement* EOF
    ;

statement
    :varDecl
    |printStmt
    |ifStmt
    ;

varDecl
    :KW_NUMBER VALID_ID OP_ASSIGN expr NEWLINE*
    |KW_TEXT VALID_ID OP_ASSIGN expr NEWLINE*
    ;

printStmt
    :KW_PRINT expr NEWLINE*
    ;

ifStmt
    :KW_IF condition code_block (KW_ELSE code_block)? NEWLINE*
    ;


code_block
 :BLOCK_START NEWLINE* statement* BLOCK_END
 ;

condition
 :expr OP_COMP expr
 ;

expr
 : expr OP_ARITHM expr        # AritmExpr
 | VALID_INT                  # IntLit
 | VALID_STRING               # StrLit
 | VALID_ID                   # VarRef
 | PAREN_START expr PAREN_END # Parens
 ;
//==============================================================================
//                                   LEXER 
//==============================================================================

// Keywords
KW_NUMBER:'number';
KW_TEXT:'text';
KW_PRINT:'print';
KW_IF:'if';
KW_ELSE:'else';

// Operators
OP_COMP:'=='|'!='|'<'|'<='|'>'|'>=';
OP_ARITHM:'+'|'-'|'*'|'/';
OP_ASSIGN:'=';

// Acceptable variable names
VALID_ID:[a-zA-Z][a-zA-Z0-9_]*;

// Acceptable variable values
VALID_INT:[0-9]+;
VALID_STRING:'"'('\\'.|~["\\])*'"';

// Scope control
BLOCK_START:'{';
BLOCK_END:'}';
PAREN_START:'(';
PAREN_END:')';

// Things to ignore
COMMENT:'//'~[\r\n]* -> skip;
WS:[ \t]+ -> skip;

// Other helpfull stuff
NEWLINE:('\r'? '\n')+;
