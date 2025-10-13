from flask import Flask, request, render_template
from src.scanner import Grammar
from src.parser import LR1

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    grammar = request.form.get('grammar', '')
    input = request.form.get('input', '')
    result = None

    if request.method == 'POST':
        try:
            g = Grammar(grammar)
            print([t.value for t in g.get_terminals()], [t.value for t in g.get_non_terminals()])
            
        except Exception as e:
            result = f"Error: {str(e)}"

    return render_template('index.html', grammar=grammar, input=input, result=result)

if __name__ == '__main__':
    app.run(debug=True, port=5002)
