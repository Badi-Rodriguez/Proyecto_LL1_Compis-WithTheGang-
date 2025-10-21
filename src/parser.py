import pandas as pd
from src.grammar import Grammar
from src.closure_table import DFAState

class ParsingTable:
    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.action = None
        self.goto = None
        self.rules = self.create_rules()
    
    def create_rules(self):
        rules = []
        start_head = self.grammar.start_symbol
        start_body = self.grammar.productions[start_head][0]
        rules.append((start_head, tuple(start_body)))

        for head in sorted(self.grammar.productions.keys()):
            if head == start_head:
                continue
            for body in self.grammar.productions[head]:
                rules.append((head, tuple(body)))
        return rules
    
    def build(self, dfa_states: list[DFAState]):
        terminals = sorted(list(self.grammar.terminals - {'ε'}))
        non_terminals = sorted(list(self.grammar.non_terminals - {self.grammar.start_symbol}))
        state_ids = [s.id for s in dfa_states]

        self.action = pd.DataFrame(columns=terminals, index=state_ids, dtype=str).fillna('')
        self.goto = pd.DataFrame(columns=non_terminals, index=state_ids, dtype=str).fillna('')

        for state in dfa_states:
            state_id = state.id

            for symbol, target_state in state.transitions.items():
                if symbol in self.grammar.terminals:
                    action = f"s{target_state.id}"
                    self.add_action(state_id, symbol, action)

            for search_symbol, item in state.reductions.items():
                rule = (item.head, item.body)
                rule_num = self.rules.index(rule)
                action = f"r{rule_num}"
                self.add_action(state_id, search_symbol, action)

            for item in state.items:
                if item.head == self.grammar.start_symbol and item.dot_pos == len(item.body):
                    action = "acc"
                    self.add_action(state_id, '$', action)

            for symbol, target_state in state.transitions.items():
                if symbol in self.grammar.non_terminals:
                    self.goto.loc[state_id, symbol] = target_state.id
        
    def add_action(self, state_id, symbol, action):
        self.action.loc[state_id, symbol] = action

    def print(self):
        if self.action is None or self.goto is None:
            return
                
        full_table = pd.concat([self.action, self.goto], axis=1).sort_index()
        print(full_table.to_markdown(tablefmt="grid"))

    def parse(self, input: str):
        processed_string = input.replace(',', ' , ')
        tokens = processed_string.split()

        input_buffer = tokens + ['$']
        stack = [0]

        steps = []
        step = 0
        while True:
            current_state = stack[-1]
            current_symbol = input_buffer[0]

            try:
                action = self.action.loc[current_state, current_symbol]
            except KeyError:
                return {"accepted": False, "error": f"No action for state {current_state} and symbol '{current_symbol}'", "steps": steps}

            steps.append({
                "step": step,
                "stack": list(stack),
                "input": list(input_buffer),
                "action": action
            })
            step += 1

            if not action:
                return {"accepted": False, "error": f"Unexpected symbol '{current_symbol}' in state {current_state}", "steps": steps}

            elif action.startswith('s'):
                next_state = int(action[1:])
                stack.append(current_symbol)
                stack.append(next_state)
                input_buffer.pop(0)

            elif action.startswith('r'):
                rule_num = int(action[1:])
                head, body = self.rules[rule_num]

                for _ in range(len(body) * 2):
                    if stack: stack.pop()

                state_before_reduction = stack[-1]
                goto_state = self.goto.loc[state_before_reduction, head]

                stack.append(head)
                stack.append(int(goto_state))

            elif action == 'acc':
                steps.append({
                    "step": step,
                    "stack": list(stack),
                    "input": list(input_buffer),
                    "action": "acc"
                })
                return {"accepted": True, "steps": steps}

            else:
                return {"accepted": False, "error": f"Unknown action '{action}'", "steps": steps}
            
    def to_json(self):
        return {
            "action": self.action.fillna("").to_dict(orient="index"),
            "goto": self.goto.fillna("").to_dict(orient="index"),
            "rules": [
                {"num": i, "head": head, "body": list(body)}
                for i, (head, body) in enumerate(self.rules)
            ]
        }