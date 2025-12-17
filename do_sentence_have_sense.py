#!/usr/bin/env python3
# coding: utf-8

'''
This is a simple script that checks if a given sentence have a semantic sense.
'''

# ==============================================================================
#                                   IMPORTS
# ==============================================================================

# Future 
from __future__ import annotations

# Python standard library
import argparse
import sys
from dataclasses import dataclass
from typing import Sequence, Optional, NoReturn

# NLTK imports
from nltk import CFG, ChartParser
from nltk.tokenize import word_tokenize
from nltk.tree.tree import Tree

# Prolog imports
from pyswip import Prolog # Install swi-prolog

# ==============================================================================
#                                CONFIGURATION 
# ==============================================================================
@dataclass(frozen=True)
class Config:

    sentence: str # Sentece that will be checked
    grammar: str # Path to file with grammar definition
    reasoning: str # Path to file with reasoning rules

    @staticmethod
    def from_args(argv: Optional[Sequence[str]]= None)-> Config:
        prsr = argparse.ArgumentParser(
                description=__doc__,
                formatter_class=argparse.RawTextHelpFormatter,
        )
        
        prsr.add_argument('sentence',
                          type=str,
                          help='Sentece that will be checked')
        prsr.add_argument('--grammar',
                          type=str,
                          default='grammar.txt',
                          help='Path to file with grammar definition')
        prsr.add_argument('--reasoning',
                          type=str,
                          default='reasoning.pl',
                          help='Path to file with reasoning rules')

        args: argparse.Namespace = prsr.parse_args(argv)

        return Config(
                sentence=args.sentence,
                grammar=args.grammar,
                reasoning=args.reasoning
        )

# ==============================================================================
#                               HELPER FUNCTIONS 
# ==============================================================================
def panic(msg: str)-> NoReturn:
    print(msg, file=sys.stderr, flush=True)
    sys.exit()

def load_grammar(filename: str)-> CFG:
    try:
        with open(filename, 'r') as grammar_file:
            grammar_str = grammar_file.read()
            return CFG.fromstring(grammar_str)
    except FileNotFoundError:
        panic(f'File {filename} not found')
    except Exception as e:
        panic(f'Unable to parse grammar file :{e}')

def prepare_semantic_query_from_sentence(sentence: str, parser:ChartParser)-> str:
    tokens = word_tokenize(sentence)
    print(f'Tokens = {tokens}')

    tree: Tree|None = None
    try:
        # For CFG there will be only one parse tree
        tree = list(parser.parse(tokens))[0]
        if tree is None:
            raise ValueError('Unknown issue')
    except ValueError as e:
        panic(f'Error whille parsing string {e}')
    tree.pretty_print()

    content = {cat:val.lower() for val, cat in tree.pos()}
    print(f'Sentence content: {content}')
    
    query= f'can_act({content['PropN']},{content['V']},{content['N']})'
    print(f'Query = {query}')
    return query


# ==============================================================================
#                                    MAIN
# ==============================================================================
def main(argv: Optional[Sequence[str]]= None)-> None:
    cfg = Config.from_args(argv)
    print(cfg)
    grammar = load_grammar(cfg.grammar)
    parser = ChartParser(grammar)
    query = prepare_semantic_query_from_sentence(cfg.sentence, parser)
    
    reasoning = Prolog()
    reasoning.consult(cfg.reasoning)
    makes_sense = list(Prolog.query(query))

    print(makes_sense)
    if makes_sense:
        print(f'Sentence {cfg.sentence} makes sense')
    else:
        print(f'Sentence {cfg.sentence} do not make sense')

if __name__ == '__main__':
    main()
