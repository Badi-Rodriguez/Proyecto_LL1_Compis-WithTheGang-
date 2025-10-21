class Grammar:
    def __init__(self):
        self.terminals = set()
        self.non_terminals = set()
        self.productions = {}
        self.start_symbol = ""

    def load(self, string: str):
        lines = [line.strip() for line in string.splitlines() if line.strip()]

        first_head = None
        for line in lines:
            if not line or "->" not in line:
                continue

            head, body = line.split("->", 1)
            head = head.strip()
            self.non_terminals.add(head)

            if first_head is None:
                first_head = head
            
            if head not in self.productions:
                self.productions[head] = []
            
            productions_str = body.split('|')
            for prod_str in productions_str:
                symbols = prod_str.strip().split()

                if not symbols or symbols == ["''"]:
                    self.productions[head].append(['ε'])
                else:
                    self.productions[head].append(symbols)
            
        if first_head is None:
            print("ERR: Las gramaticas no son validas.")
            return False
        
        all_symbols = set(sym for prods in self.productions.values() for prod in prods for sym in prod)
        self.terminals = all_symbols - self.non_terminals
        self.terminals.add('$')

        # Add additional non-terminal for S'
        self.start_symbol = first_head + "'"
        self.non_terminals.add(self.start_symbol)

        self.productions[self.start_symbol] = [[first_head]]

        return True
    
    def first(self, symbol: str, visited = None):
        if visited is None:
            visited = set()

        if symbol in visited:
            return set()

        if symbol in self.terminals or symbol == 'ε':
            return { symbol }
        
        if symbol not in self.non_terminals:
            return set()
        
        visited.add(symbol)
        first_symbols = set()
        prods = self.productions[symbol]

        if not prods:
            visited.remove(symbol)
            return set()
        
        for prod in prods:
            add_epsilon = True
            for sym in prod:
                sym_first = self.first(sym, visited)
                first_symbols.update(s for s in sym_first if s != 'ε')
                if 'ε' not in sym_first:
                    add_epsilon = False
                    break

            if add_epsilon:
                first_symbols.add('ε')

        visited.remove(symbol)
        return first_symbols
    
    def first_sequence(self, sequence: tuple, visited = None):
        if visited is None:
            visited = set()

        if not sequence:
            return {'ε'}

        first_symbols = set()
        add_epsilon = True

        for sym in sequence:
            sym_first = self.first(sym, visited)
            first_symbols.update(s for s in sym_first if s != 'ε')

            if 'ε' not in sym_first:
                add_epsilon = False
                break

        if add_epsilon:
            first_symbols.add('ε')

        return first_symbols
    
    def to_json(self):
        first_table = {
            nt: sorted(list(self.first(nt)))
            for nt in sorted(self.non_terminals)
        }

        return {
            "start_symbol": self.start_symbol,
            "non_terminals": sorted(list(self.non_terminals)),
            "terminals": sorted(list(self.terminals)),
            "productions": {
                head: [" ".join(body) for body in bodies]
                for head, bodies in self.productions.items()
            },
            "first": first_table
        }
