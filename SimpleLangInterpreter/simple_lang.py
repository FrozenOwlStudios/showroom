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
from typing import Sequence, Optional


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
#                                    MAIN
# ==============================================================================
def main(argv: Optional[Sequence[str]]= None)-> None:
    cfg = Config.from_args(argv)
    print(cfg)
