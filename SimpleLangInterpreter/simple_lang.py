#!/usr/bin/env python3
# coding: utf-8

'''
An interpreter for a simple script language.
'''

# ==============================================================================
#                                   IMPORTS
# ==============================================================================

# Future 
from __future__ import annotations

# Python standard library
import argparse
from dataclasses import dataclass
from typing import Sequence, Optional, Any, Dict

# ANTLLR 4 general imports
from antlr4 import FileStream, CommonTokenStream, InputStream
from antlr4.error.ErrorListener import ErrorListener

# ANTLLR 4 grammar
from antlr_grammar.SimpleLangGrammarLexer import SimpleLangGrammarLexer
from antlr_grammar.SimpleLangGrammarParser import SimpleLangGrammarParser
from antlr_grammar.SimpleLangGrammarVisitor import SimpleLangGrammarVisitor


# ==============================================================================
#                                CONFIGURATION 
# ==============================================================================
@dataclass(frozen=True)
class Config:

    script_file: str # Path to file with script in simple lang 

    @staticmethod
    def from_args(argv: Optional[Sequence[str]]= None)-> Config:
        prsr = argparse.ArgumentParser(
                description=__doc__,
                formatter_class=argparse.RawTextHelpFormatter,
        )
        
        prsr.add_argument('script_file',
                          type=str,
                          help='Path to file with script in simple lang')

        args: argparse.Namespace = prsr.parse_args(argv)

        return Config(script_file=args.script_file)

# ==============================================================================
#                             SIMPLE LANG INTERPRETER 
# ==============================================================================
class ThrowingErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e) -> None:
        raise SyntaxError(f'line {line}:{column} -> {msg}')

@dataclass
class Variable:
    kind: str # either "number" or "text"
    value: Any

COMPARITION_OPERATORS = {
    '==': lambda l,r: l==r,
    '!=': lambda l,r: l!=r,
    '<': lambda l,r: l<r,
    '>': lambda l,r: l>r,
    '>=': lambda l,r: l>=r,
    '<=': lambda l,r: l<=r
}

ARITHMETIC_OPERATORS = {
    '+': lambda l,r: l+r,
    '-': lambda l,r: l-r,
    '*': lambda l,r: l*r,
    '/': lambda l,r: l/r
}

class SimpleLangInterpreter(SimpleLangGrammarVisitor):

    env: Dict[str,Variable]

    def __init__(self)-> None:
        self.env = {}

    def visitProgram(self, ctx: SimpleLangGrammarParser.ProgramContext):
        for statement in ctx.statement():
            self.visit(statement)
        return None

    def visitVarDecl(self, ctx: SimpleLangGrammarParser.VarDeclContext):
        name = ctx.VALID_ID().getText()
        expr_val = self.visit(ctx.expr())

        if ctx.KW_NUMBER() is not None and expr_val.kind != 'number':
            raise TypeError(f'Assigning a non numerical value to numeric variable')
        elif ctx.KW_TEXT() is not None and  expr_val.kind != 'text':
            raise TypeError(f'Attempting to assign non text value to text variable')
        print(f'VAL {name} == {expr_val}')
        self.env[name] = expr_val
        return None

    def visitPrintStmt(self, ctx: SimpleLangGrammarParser.PrintStmtContext):
        expr_val = self.visit(ctx.expr())
        print(expr_val.value)
        return None

    def visitIfStmt(self, ctx: SimpleLangGrammarParser.IfStmtContext):
        cond = self.visit(ctx.condition())
        if cond:
            self.visit(ctx.code_block(0))
        elif ctx.KW_ELSE() is not None:
            self.visit(ctx.code_block(1))
        return None

    def visitCode_block(self, ctx: SimpleLangGrammarParser.Code_blockContext):
        for statement in ctx.statement():
            self.visit(statement)
        return None

    def visitCondition(self, ctx: SimpleLangGrammarParser.ConditionContext):
        l = self.visit(ctx.expr(0))
        r = self.visit(ctx.expr(1))
        op = ctx.OP_COMP().getText()
        
        if l.kind != 'number' or r.kind != 'number':
            raise TypeError('Only numbers can be compared')
        return COMPARITION_OPERATORS[op](l.value,r.value)

    def visitAritmExpr(self, ctx: SimpleLangGrammarParser.AritmExprContext):
        l = self.visit(ctx.expr(0))
        r = self.visit(ctx.expr(1))
        op = ctx.OP_ARITHM().getText()

        if l.kind != 'number' or r.kind != 'number':
            raise TypeError('Only numbers can be calculated')

        return ARITHMETIC_OPERATORS[op](l.value,r.value)

    def visitParens(self, ctx: SimpleLangGrammarParser.ParensContext):
        return self.visit(ctx.expr())

    def visitStrLit(self, ctx: SimpleLangGrammarParser.StrLitContext):
        raw = ctx.VALID_STRING().getText()
        s = bytes(raw[1:-1],'utf-8').decode('unicode_escape')
        return Variable('text',s)

    def visitIntLit(self, ctx: SimpleLangGrammarParser.IntLitContext):
        return Variable('number', int(ctx.VALID_INT().getText()))

    def visitVarRef(self, ctx: SimpleLangGrammarParser.VarRefContext):
        name = ctx.VALID_ID().getText()
        if name not in self.env:
            raise KeyError(f'Variable "{name}" not found')
        return self.env[name]


# ==============================================================================
#                                    MAIN
# ==============================================================================
def main(argv: Optional[Sequence[str]]= None)-> None:
    cfg = Config.from_args(argv)
    code = ''
    with open(cfg.script_file, 'r') as f:
        code = f.read()

    lexer = SimpleLangGrammarLexer(InputStream(code))
    stream = CommonTokenStream(lexer)
    parser = SimpleLangGrammarParser(stream)

    lexer.removeErrorListeners()
    parser.removeErrorListeners()
    lexer.addErrorListener(ThrowingErrorListener())
    parser.addErrorListener(ThrowingErrorListener())
    tree = parser.program()
    interpreter = SimpleLangInterpreter()
    interpreter.visit(tree)


if __name__ == '__main__':
#    try:
    main()
#    except Exception as e:
#        print(e)
