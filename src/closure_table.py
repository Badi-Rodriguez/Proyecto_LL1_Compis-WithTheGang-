from src.grammar import Grammar

class LRItem():
    def __init__(self, head: str, body: tuple, search_symbol, dot_position = 0):
        self.head = head
        self.body = body
        self.search_symbol = search_symbol
        self.dot_pos = dot_position
    
    def __str__(self):
        body_list = list(self.body)
        body_list.insert(self.dot_pos, '•')
        return f"[{self.head} -> {' '.join(body_list)}, {self.search_symbol}]"

    def __eq__(self, other):
        if not isinstance(other, LRItem):
            return NotImplemented
        return (self.head == other.head and
                self.body == other.body and
                self.dot_pos == other.dot_pos and
                self.search_symbol == other.search_symbol)

    def __hash__(self):
        return hash((self.head, self.body, self.dot_pos, self.search_symbol))

class NFAState:
    ID_COUNTER = 0

    def __init__(self, item: LRItem):
        self.id = NFAState.ID_COUNTER
        self.epsilon_transitions = set()
        self.transitions = {}
        self.item = item

        NFAState.ID_COUNTER += 1

    def __repr__(self):
        return f"State({self.id}, Item: {self.item})"
    
class NFABuilder:
    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.states = {}

    def get_or_create_state(self, item: LRItem):
        if item not in self.states:
            self.states[item] = NFAState(item)
        return self.states[item]

    def build(self):
        NFAState.ID_COUNTER = 0

        initial_item = LRItem(
            head=self.grammar.start_symbol, 
            body=tuple(self.grammar.productions[self.grammar.start_symbol][0]), 
            search_symbol='$',
            dot_position=0
        )

        start_state = self.get_or_create_state(initial_item)
        state_stack = [start_state]
        processed = set()

        while state_stack:
            curr_state: NFAState = state_stack.pop(0)
            item = curr_state.item

            if item in processed:
                continue
            processed.add(item)

            if item.dot_pos >= len(item.body):
                continue

            symbol_after_dot = item.body[item.dot_pos]

            next_item = LRItem(item.head, item.body, item.search_symbol, item.dot_pos + 1)
            target_state_symbol = self.get_or_create_state(next_item)
            curr_state.transitions[symbol_after_dot] = target_state_symbol

            if next_item not in processed:
                state_stack.append(target_state_symbol)

            if symbol_after_dot in self.grammar.non_terminals:
                beta_a_sequence = item.body[item.dot_pos + 1:] + (item.search_symbol,)
                new_search_symbols = self.grammar.first_sequence(beta_a_sequence)

                for b_prod_body in self.grammar.productions[symbol_after_dot]:
                    for new_search_symbol in new_search_symbols:
                        if new_search_symbol == 'ε': 
                            continue
                        
                        target_item_epsilon = LRItem(symbol_after_dot, tuple(b_prod_body), new_search_symbol, 0)
                        target_state_epsilon = self.get_or_create_state(target_item_epsilon)
                        curr_state.epsilon_transitions.add(target_state_epsilon)

                        if target_item_epsilon not in processed:
                            state_stack.append(target_state_epsilon)
            
        return list(self.states.values())
    
class DFAState:
    ID_COUNTER = 0

    def __init__(self, nfa_states: set):
        self.id = DFAState.ID_COUNTER

        self.nfa_states = nfa_states
        self.items = frozenset(s.item for s in nfa_states)
        self.transitions = {}
        self.reductions = {}

        DFAState.ID_COUNTER += 1

    def __repr__(self):
        return f"DFA_State(I{self.id})"
    
    def to_json(self):
        return {
            "id": self.id,
            "items": [
                {
                    "head": item.head,
                    "body": list(item.body),
                    "dot_pos": item.dot_pos,
                    "search_symbol": item.search_symbol
                }
                for item in self.items
            ],
            "transitions": {sym: target.id for sym, target in self.transitions.items()},
            "reductions": {
                sym: {
                    "head": item.head,
                    "body": list(item.body)
                } for sym, item in self.reductions.items()
            }
        }
    
class DFABuilder:
    def __init__(self, grammar: Grammar, nfa_start_state: NFAState):
        self.grammar = grammar
        self.nfa_start_state = nfa_start_state
        self.states = {}

    def get_epsilon_closure(self, nfa_states: set):
        closure = set(nfa_states)
        state_stack = list(nfa_states)

        while state_stack:
            curr_state: NFAState = state_stack.pop(0)
            for target_state in curr_state.epsilon_transitions:
                if target_state not in closure:
                    closure.add(target_state)
                    state_stack.append(target_state)
        return closure
    
    def get_or_create_state(self, nfa_states: set):
        items_set = frozenset(s.item for s in nfa_states)
        if items_set in self.states:
            return self.states[items_set]

        new_state = DFAState(nfa_states)
        
        for item in new_state.items:
            if item.dot_pos == len(item.body):
                if item.head != self.grammar.start_symbol:
                    new_state.reductions[item.search_symbol] = item
        
        self.states[items_set] = new_state
        return new_state
    
    def build(self):
        DFAState.ID_COUNTER = 0

        initial_closure = self.get_epsilon_closure({self.nfa_start_state})
        initial_dfa_state = self.get_or_create_state(initial_closure)
        
        state_stack = [initial_dfa_state]
        processed = set()
        all_states = []

        while state_stack:
            curr_dfa_state = state_stack.pop(0)
            if curr_dfa_state in processed:
                continue
                
            processed.add(curr_dfa_state)
            all_states.append(curr_dfa_state)

            possible_symbols = set()
            for nfa_state in curr_dfa_state.nfa_states:
                possible_symbols.update(nfa_state.transitions.keys())

            for symbol in possible_symbols:
                move_set = set()
                for nfa_state in curr_dfa_state.nfa_states:
                    if symbol in nfa_state.transitions:
                        move_set.add(nfa_state.transitions[symbol])
                
                target_closure = self.get_epsilon_closure(move_set)
                if not target_closure:
                    continue

                target_dfa_state = self.get_or_create_state(target_closure)
                curr_dfa_state.transitions[symbol] = target_dfa_state
                
                if target_dfa_state not in processed:
                    state_stack.append(target_dfa_state)

        return list(processed)

    def to_json(self):
        return [state.to_json() for state in self.states.values()]
