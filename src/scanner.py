from typing import List
from enum import Enum

class SymbolType(Enum):
    TERMINAL = 0
    NON_TERMINAL = 1

class Symbol:
    def __init__(self, value, type):
        self.value: str = value
        self.type: SymbolType = type if type else SymbolType.TERMINAL

    def __eq__(self, other):
        return isinstance(other, Symbol) and self.value == other.value and self.type == other.type

    def __hash__(self):
        return hash((self.value, self.type))
    
    def __repr__(self):
        if self.value == '':
            return '"ε"'
        return f'"{self.value}"' if self.type == SymbolType.TERMINAL else self.value

class GrammarRule:
    def __init__(self, start_symbol: Symbol):
        self.start_symbol: Symbol = start_symbol
        self.productions: List[List[Symbol]] = []
    
    def add_prod(self, prod: List[Symbol]):
        self.productions.append(prod)

    def __repr__(self):
        prods_str = " | ".join(" ".join(map(str, p)) for p in self.productions)
        return f"{self.start_symbol} -> {prods_str}"

class Grammar:
    def __init__(self, string: str):
        self.rules: List[GrammarRule] = []

        string_rules = [line.strip() for line in string.splitlines() if line.strip()]

        for line in string_rules:
            if "->" not in line:
                continue

            left_side, right_side = line.split("->", 1)
            left_side = left_side.strip()

            symbol = Symbol(left_side, SymbolType.NON_TERMINAL)
            rule = self.find_or_create_rule(symbol)

            options = [opt.strip() for opt in right_side.split('|')]
            for option in options:
                if not option:
                    continue

                symbols = []
                tokens = option.split()

                for token in tokens:
                    if token.startswith('"') and token.endswith('"'):
                        symbols.append(Symbol(token.replace('"', ''), SymbolType.TERMINAL))
                    else:
                        symbols.append(Symbol(token, SymbolType.NON_TERMINAL))

                rule.add_prod(symbols)
    
    def find_or_create_rule(self, start_symbol: Symbol):
        for rule in self.rules:
            if rule.start_symbol.value == start_symbol.value:
                return rule
        
        new_rule = GrammarRule(start_symbol)
        self.rules.append(new_rule)
        return new_rule
    
    def get_prods(self, start_symbol: Symbol):
        for i in self.rules:
            if i.start_symbol.value == start_symbol.value:
                return i.productions

    def get_all_symbols(self):
        symbols = set()

        for rule in self.rules:
            symbols.add(rule.start_symbol)
            for prod in rule.productions:
                symbols.update(prod)
        
        return symbols
    
    def get_terminals(self):
        return { s for s in self.get_all_symbols() if s.type == SymbolType.TERMINAL }
    
    def get_non_terminals(self):
        return { s for s in self.get_all_symbols() if s.type == SymbolType.NON_TERMINAL }

    def first(self, symbol: Symbol):
        if symbol.type == SymbolType.TERMINAL or symbol.value == '':
            return { symbol }
        
        first_symbols = set()
        prods = self.get_prods(symbol)
        if not prods:
            return { Symbol('', SymbolType.TERMINAL) }
        
        for prod in prods:
            add_epsilon = True
            for sym in prod:
                sym_first = self.first(sym)
                for s in sym_first:
                    if s.value != '':
                        first_symbols.add(s)

                if all(s.value != '' for s in sym_first):
                    add_epsilon = False
                    break

            if add_epsilon:
                first_symbols.add(Symbol('', SymbolType.TERMINAL))

        return first_symbols
    
    def follow(self):
        return

    def __repr__(self):
        return "\n".join(str(rule) for rule in self.rules)