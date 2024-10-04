from flask import Flask, render_template, request, redirect, url_for
import re  # Importar la librería de expresiones regulares

app = Flask(__name__)

# Definir los tokens para el análisis léxico
lexical_tokens = {
    'for': 'Reservada For',
    'do': 'Reservada Do',
    'while': 'Reservada While',
    'if': 'Reservada If',
    'else': 'Reservada Else',
    'int': 'Tipo Entero',
    'float': 'Tipo Flotante',
    'char': 'Tipo Carácter',
    'string': 'Tipo Cadena',
}

# Historial de tokens analizados
lexical_history = []
syntactic_history = []

@app.route('/')
def index():
    return render_template('index.html', lexical_results=[], syntactic_results=[], code="")

@app.route('/lexical', methods=['POST'])
def lexical_analysis():
    text = request.form['code']
    lines = text.splitlines()
    lexical_results = []

    # Expresiones regulares para identificar diferentes tipos de tokens
    token_patterns = {
        'Cadena': r'"([^"]*)"',      # Cadenas entre comillas
        'Identificador': r'\b[a-zA-Z_][a-zA-Z0-9_]*\b',  # Identificadores
        'Numero': r'\b\d+(\.\d+)?\b', # Números enteros y flotantes
        'Simbolo': r'[{}();,]',       # Símbolos (incluyendo el punto y coma)
        'Reserveda': '|'.join(re.escape(key) for key in lexical_tokens.keys())  # Palabras reservadas
    }

    # Unir todas las expresiones en una sola
    token_regex = '|'.join(f'(?P<{key}>{pattern})' for key, pattern in token_patterns.items())

    for i, line in enumerate(lines, start=1):
        for match in re.finditer(token_regex, line):
            token_type = match.lastgroup
            token_value = match.group(token_type)

            token_info = {
                'token': token_value,
                'pr': 'X' if token_type == 'Reserveda' else '',
                'id': 'X' if token_type == 'Identificador' else '',
                'cad': 'X' if token_type == 'Cadena' else '',
                'num': 'X' if token_type == 'Numero' else '',
                'simbolo': 'X' if token_type == 'Simbolo' else '',
                'tipo': lexical_tokens.get(token_value, token_type.capitalize())
            }
            lexical_results.append(token_info)
            lexical_history.append(token_info)

    return render_template('index.html', lexical_results=lexical_results, syntactic_results=[], code=text)

@app.route('/syntactic', methods=['POST'])
def syntactic_analysis():
    text = request.form['code']
    lines = text.splitlines()
    syntactic_results = []

    for i, line in enumerate(lines, start=1):
        syntactic_info = {
            'linea': i,
            'detalle': 'Sintaxis válida'  # Este es un ejemplo simple
        }
        syntactic_results.append(syntactic_info)
        syntactic_history.append(syntactic_info)

    return render_template('index.html', lexical_results=[], syntactic_results=syntactic_results, code=text)

@app.route('/clear', methods=['POST'])
def clear():
    lexical_history.clear()
    syntactic_history.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
