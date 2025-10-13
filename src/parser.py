from src.scanner import Symbol, Production, Grammar
from typing import List, Dict

class GrammarRuleLR():
    def __init__(self, start_symbol: Symbol, production: Production, search_symbol: Symbol):
        self.start_symbol: Symbol = start_symbol
        self.production: Production = production
        self.search_symbol: Symbol = search_symbol
        self.dot_pos: int = 0

class State:
    def __init__(self):
        self.id: int = 0
        self.rules: List[GrammarRuleLR]
        self.transitions: List[Dict[Symbol, State]]

class LR1:
    def __init__(self, grammar):
        self.grammar: Grammar = grammar

    def parse(self, input):
        return ''