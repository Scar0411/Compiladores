from flask import Flask, render_template, request, redirect, url_for
import re

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
    return render_template('index.html', lexical_results=[], syntactic_results=[], counters=None, code="", syntax_errors="", syntactic_result="")

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
    }

    # Expresión regular para las palabras reservadas
    reserved_words_pattern = r'\b(?:' + '|'.join(re.escape(key) for key in lexical_tokens.keys()) + r')\b'

    # Unir todas las expresiones en una sola
    token_regex = '|'.join(f'(?P<{key}>{pattern})' for key, pattern in token_patterns.items()) + f'|(?P<Reservada>{reserved_words_pattern})'

    # Inicializar los contadores
    counters = {
        'Reservada': 0,
        'Identificador': 0,
        'Cadena': 0,
        'Numero': 0,
        'Simbolo': 0,
        'Total': 0  # Contador para el total de tokens
    }

    for i, line in enumerate(lines, start=1):
        for match in re.finditer(token_regex, line):
            token_type = match.lastgroup
            token_value = match.group(token_type)

            token_info = {
                'linea': i,  # Añadimos el número de línea
                'token': token_value,
                'pr': 'X' if token_type == 'Reservada' else '',
                'id': 'X' if token_type == 'Identificador' else '',
                'cad': 'X' if token_type == 'Cadena' else '',
                'num': 'X' if token_type == 'Numero' else '',
                'simbolo': 'X' if token_type == 'Simbolo' else '',
                'tipo': lexical_tokens.get(token_value, token_type.capitalize())
            }
            lexical_results.append(token_info)
            lexical_history.append(token_info)

            # Incrementar los contadores según el tipo de token
            counters[token_type] += 1
            counters['Total'] += 1  # Incrementar el total de tokens

    return render_template('index.html', lexical_results=lexical_results, syntactic_results=[], counters=counters, code=text)

@app.route('/syntactic', methods=['POST'])
def syntactic_analysis():
    text = request.form['code']
    lines = text.splitlines()
    syntax_errors = []
    syntactic_result = ""  # Nueva variable para indicar resultado sintáctico

    # Aquí aplicamos las reglas de errores sintácticos
    declared_variables = set()
    int_declared = False  # Bandera para verificar si se ha declarado 'int'

    # 1. Verificar la llave de inicio '{' solo en la primera línea
    if lines and '{' not in lines[0]:
        syntax_errors.append("Error de sintaxis: Falta la llave de inicio '{' al inicio del bloque.")
    
    # 2. Verificar la llave de cierre '}' solo en la última línea
    if lines and '}' not in lines[-1]:
        syntax_errors.append("Error de sintaxis: Falta la llave de cierre '}' al final del bloque.")
    
    # Variables esperadas
    expected_variables = {'a', 'b', 'c'}
    
    # Recorrer las líneas de código para otros errores
    for i, line in enumerate(lines):
        # Comprobar declaración de variables
        if 'int' in line:  # Verificar si se declara 'int'
            int_declared = True
            # Extraer variables de la declaración
            declared_vars = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', line)
            declared_variables.update(declared_vars)

        # Comprobar uso de variables no declaradas
        if 'read' in line:
            variable = re.search(r'read\s+(\w+)', line)
            if variable and variable.group(1) not in declared_variables:
                syntax_errors.append(f"Error: identificador '{variable.group(1)}' en la instrucción 'read' no declarado.")

        # Comprobar operación de suma
        if '=' in line:
            left_side = line.split('=')[0]
            if '+' in left_side:
                operands = re.split(r'\s*\+\s*', left_side)
                for operand in operands:
                    operand = operand.strip()
                    if not (re.match(r'^\d+$', operand) or operand in declared_variables):
                        syntax_errors.append(f"Error de sintaxis en la línea {i+1}: Token inesperado '+'.")
                        break

        # Comprobar uso de variables no declaradas al asignar
        if '=' in line:
            right_side = line.split('=')[1]
            for variable in declared_variables:
                if variable not in right_side and variable != '1' and re.match(r'^\d+$', variable):
                    syntax_errors.append(f"Error: variable '{variable}' no definida en la línea {i+1}.")
        
    # Verificar si faltan las variables 'a', 'b', 'c' en la declaración
    missing_variables = expected_variables - declared_variables
    for var in missing_variables:
        syntax_errors.append(f"Error de sintaxis: Variable no definida para '{var}'.")

    # Verificar si falta la palabra reservada 'int' o no ha sido declarada
    if not int_declared:  # Se asegura de verificar si 'int' fue declarado
        syntax_errors.append("Error: palabra reservada 'int' no declarada.")

    # Si no hay errores, establecer el resultado sintáctico correcto
    if not syntax_errors:
        syntactic_result = "Resultado Sintáctico Correcto"

    return render_template('index.html', lexical_results=[], syntactic_results=[], counters=None, code=text, syntax_errors="\n".join(syntax_errors), syntactic_result=syntactic_result)

@app.route('/clear', methods=['POST'])
def clear():
    lexical_history.clear()
    syntactic_history.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
