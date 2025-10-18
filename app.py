from flask import Flask, request, jsonify
from src.grammar import Grammar
from src.closure_table import NFABuilder, DFABuilder
from src.parser import ParsingTable
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400

    grammar_input = data.get('grammar', '')
    input_str = data.get('input', '')

    if not grammar_input.strip():
        return jsonify({"error": "Grammar is required"}), 400

    grammar = Grammar()
    grammar.load(grammar_input)

    nfa_builder = NFABuilder(grammar)
    nfa_states = nfa_builder.build()

    dfa_builder = DFABuilder(grammar, nfa_states[0])
    dfa_states = dfa_builder.build()

    parsing_table = ParsingTable(grammar)
    parsing_table.build(dfa_states)

    result = parsing_table.parse(input_str)

    response_data = {
        "grammar": grammar.to_json(),
        "dfa": [s.to_json() for s in dfa_states],
        "parsing_table": parsing_table.to_json(),
        "parse_result": result
    }

    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True, port=5002)
