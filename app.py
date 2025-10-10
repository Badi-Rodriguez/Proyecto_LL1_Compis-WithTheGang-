from flask import Flask, request, render_template
from lark import Lark, UnexpectedInput
from src.utils import grammar_to_lark

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    grammar = request.form.get('grammar', '')
    input = request.form.get('input', '')
    result = None

    if request.method == 'POST':
        try:
            start_symbol, lark_grammar = grammar_to_lark(grammar)
            l = Lark(lark_grammar, start=start_symbol)

            tree = l.parse(input)
            result = tree.pretty()
            
        except UnexpectedInput as e:
            result = f"Parse error: {str(e)}"
        except Exception as e:
            result = f"Error: {str(e)}"

    return render_template('index.html', grammar=grammar, input=input, result=result)

if __name__ == '__main__':
    app.run(debug=True, port=5002)
