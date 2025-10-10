"""
ToDo: Hacer funcion grammar_to_lark()
Lark tiene un formato especial para detectar gramaticas:

    NORMAL:
    A -> B | 2
    B -> 1 

    LARK:
    a: b | "2"
    b: "1"

Basicamente, se cambian los -> por : , todos los no-terminales deben estar en minuscula, 
y todos los terminales deben tener "" para que sean identificados como terminales
"""

def grammar_to_lark(grammar):
    result = grammar.replace('->', ':')
    start_symbol = 'a' # ToDo: Que atomaticamente utilice primer no-terminar como start_symbol

    return start_symbol, result