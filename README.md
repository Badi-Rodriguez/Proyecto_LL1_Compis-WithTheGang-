# LR(1) Parser for CS3025 @ UTEC

¡Hecho! Te dejo ambas piezas listas para pegar. Mantengo el **título en inglés** y todo lo demás en español.

---

# LR(1) Parser Service — CS3025 @ UTEC

Un servicio web pequeño que recibe una gramática libre de contexto y una cadena de entrada, construye el autómata y la tabla de parseo estilo LR, y devuelve un JSON completo: metadatos de la gramática (incluyendo conjuntos FIRST), estados del DFA, tabla de parseo y resultado del parseo.

> **Pipeline (un solo endpoint):** Grammar → NFA → DFA → Parsing Table → Parse  
> Implementado en `POST /analyze`. Retorna `{ grammar, dfa, parsing_table, parse_result }`.

## Características
- Parseo de reglas en formato `A -> α | β`.
- Cálculo de conjuntos **FIRST** y exportación de la gramática como JSON.
- Construcción del **DFA** (colección canónica de items) vía `closure/goto`.
- Generación de **tabla de parseo** y verificación de la cadena de entrada.
- Un único endpoint HTTP con CORS habilitado; JSON in/out.

## API

**POST** `/analyze`

**Request (JSON)**
```json
{
  "grammar": "E -> E + T | T\nT -> T * F | F\nF -> ( E ) | id",
  "input": "id + id * id"
}
````

**Response (forma general)**

```json
{
  "grammar": {
    "start_symbol": "S'",
    "non_terminals": ["..."],
    "terminals": ["...", "$"],
    "productions": { "A": ["α", "β"], "S'": ["S"] },
    "first": { "A": ["a", "ε"], "...": ["..."] }
  },
  "dfa": [{ "...": "..." }],
  "parsing_table": { "...": "..." },
  "parse_result": { "accepted": true, "trace": ["..."] }
}
```

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install flask flask-cors

# run
python app.py  # o: python -m flask --app app run -p 5002

# test
curl -X POST http://127.0.0.1:5002/analyze \
  -H 'Content-Type: application/json' \
  -d '{"grammar":"E -> E + T | T\nT -> T * F | F\nF -> ( E ) | id", "input":"id + id * id"}'
```

## Estructura del proyecto

```
app.py               # POST /analyze: orquesta todo el pipeline
src/
  grammar.py         # Carga de gramática + FIRST, FIRST(sequence), to_json
  closure_table.py   # NFABuilder, DFABuilder (closure/goto de items)
  parser.py          # Construcción de tabla + parse()
```

## Notas

* Se construye la gramática aumentada con `S' -> S` y se incluye `$` como EOF en los terminales.
* `grammar.to_json()` incluye FIRST, terminales/no terminales y producciones (stringificadas).

## Roadmap (sugerido)

* Añadir FOLLOW y validación LL(1)/LR(1).
* Reportar conflictos (shift/reduce, reduce/reduce) en el JSON.
* Carpeta de ejemplos: gramáticas mínimas + trazas esperadas.
* Tests unitarios para gramática, closure/goto y aceptación de parseo.

## Licencia

MIT (sugerida). Agrega un archivo `LICENSE` si el curso lo requiere.

---

# LR(1) Parser Service — Technical Report

## 1. Resumen
El servicio expone un único endpoint HTTP que recibe una gramática (CFG) y una cadena de entrada, luego:
1) carga y **aumenta** la gramática,  
2) construye el autómata de **items** (closure/goto),  
3) genera la **tabla de parseo**, y  
4) intenta **parsear** la cadena, devolviendo un JSON con todos los artefactos (grammar/DFA/tabla/resultado).

## 2. Representación de la gramática
- Formato de entrada: una producción por línea `A -> α | β` (alternativas separadas por `|`).
- No terminales: símbolos del lado izquierdo (LHS).  
  Terminales: símbolos del RHS que no son no terminales; se añade `$` como fin de entrada.
- Gramática aumentada con `S' -> S` para el estilo LR.  
- Se implementa `first(X)` y `first(α1 α2 ... αk)`; FIRST de una secuencia propaga `ε` mientras corresponda.  
- `to_json()` exporta:
  - `start_symbol`, `non_terminals`, `terminals`, `productions` (stringificadas),
  - `first`: conjuntos FIRST por no terminal.

## 3. Autómata y tabla de parseo
- **NFA/Closure**: a partir de la gramática se inicializa la colección de estados.
- **DFA (colección canónica)**: se determiniza con `goto` sobre conjuntos de items.
- **Tabla de parseo**: a partir del DFA se generan entradas **ACTION/GOTO** (familia LR).
- **Parseo end-to-end**: la entrada se valida consultando la tabla; el resultado indica aceptación y, opcionalmente, traza.

### Contrato de datos

**Request**
```json
{
  "grammar": "A -> a A | ε\nS -> A",
  "input": "a a a"
}
````

**Response**

```json
{
  "grammar": { "...": "campos descritos arriba" },
  "dfa": [{ "...": "codificación de estados" }],
  "parsing_table": { "...": "ACTION/GOTO o equivalente" },
  "parse_result": { "accepted": true, "trace": ["..."] }
}
```

**Campos del JSON de gramática**

* `start_symbol: string` — inicio aumentado (e.g. `S'`)
* `non_terminals: string[]`
* `terminals: string[]` — incluye `$` como EOF
* `productions: { head: string[] }`
* `first: { non_terminal: string[] }`

## 4. Complejidad (alto nivel)

Sean `|G|` el total de símbolos/producciones y `|I|` el número de conjuntos de items (estados del DFA).

* **FIRST**: en peor caso ~`O(|G|^2)` por la propagación sobre producciones.
* **Closure/Goto & DFA**: hasta `O(|I| * |G|)` expansiones; el tamaño práctico depende de ambigüedad de la gramática.
* **Construcción de tabla**: proporcional a `|I| × |Σ|` (símbolos de gramática).
* **Parseo**: lineal en la longitud de la entrada (lookups en la tabla).

## 5. Validación y pruebas (sugeridas)

* Unit tests para `first()` y `first_sequence()` con y sin `ε`.
* Golden tests para gramáticas pequeñas (paréntesis balanceados, aritmética simple).
* Verificación de determinismo del DFA (sin estados duplicados).
* Sanidad de tabla: detectar y reportar conflictos (shift/reduce, reduce/reduce).

