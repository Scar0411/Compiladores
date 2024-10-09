from flask import Flask, render_template, request
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lexical', methods=['POST'])
def lexical_analysis():
    text = request.form['code']
    lines = text.splitlines()  # Dividir el código en líneas
    lexical_results = []
    
    # Contadores para los tipos de tokens
    counters = {
        'Reservada': 0,
        'Identificador': 0,
        'Cadena': 0,
        'Numero': 0,
        'Simbolo': 0,
        'Total': 0,
    }

    # Palabras reservadas
    reserved_words = {'public', 'class', 'static', 'void', 'main', 'System.out.println'}
    
    # Expresiones regulares para detectar tokens
    token_patterns = {
        'Reservada': r'\b(?:public|class|static|void|main)\b',
        'Identificador': r'\b[a-zA-Z_][a-zA-Z0-9_]*\b',
        'Cadena': r'\".*?\"',
        'Numero': r'\b\d+\b',
        'Simbolo': r'[{}();\[\]]'  # Incluye [ y ]
    }
    
    # Analizar línea por línea
    for line_number, line in enumerate(lines, start=1):
        # Eliminar espacios en blanco innecesarios
        stripped_line = line.strip()
        tokens_found = []

        # Encontrar y clasificar tokens usando las expresiones regulares
        for token_type, pattern in token_patterns.items():
            matches = re.finditer(pattern, stripped_line)
            for match in matches:
                token_value = match.group(0)
                tokens_found.append({
                    'linea': line_number,
                    'token': token_value,
                    'tipo': token_type
                })
                counters[token_type] += 1
                counters['Total'] += 1

        # Agregar los tokens encontrados a los resultados léxicos
        lexical_results.extend(tokens_found)

    # Generar los resultados para el renderizado
    return render_template('index.html', lexical_results=lexical_results, counters=counters, code=text)

@app.route('/syntactic', methods=['POST'])
def syntactic_analysis():
    text = request.form['code']
    lines = text.splitlines()  # Dividir el código en líneas
    syntax_errors = []

    # Verificar que la estructura esperada esté presente
    expected_structure = [
        "public class HolaMundo {",
        "public static void main(string [] {",
        "System.out.println(\"Hola mundo\");",
        "}"
    ]

    # Contador para saber si se encontró cada línea esperada
    found_lines = {line: False for line in expected_structure}

    # Contar las llaves, corchetes y comillas de apertura y cierre
    opening_brace_count = sum(line.count('{') for line in lines)
    closing_brace_count = sum(line.count('}') for line in lines)
    opening_bracket_count = sum(line.count('[') for line in lines)
    closing_bracket_count = sum(line.count(']') for line in lines)
    opening_quote_count = sum(line.count('"') for line in lines)

    # Comprobar si faltan llaves, corchetes o comillas
    if opening_brace_count == 0:
        syntax_errors.append("Error de sintaxis: falta la llave de inicio '{'.")
    if closing_brace_count == 0:
        syntax_errors.append("Error de sintaxis: falta la llave de cierre '}'.")
    if opening_brace_count != closing_brace_count:
        syntax_errors.append("Error de sintaxis: número de llaves de apertura y cierre no coincide.")
    
    if opening_bracket_count == 0:
        syntax_errors.append("Error de sintaxis: falta el corchete de inicio '['.")
    if closing_bracket_count == 0:
        syntax_errors.append("Error de sintaxis: falta el corchete de cierre ']'.")

    if opening_quote_count % 2 != 0:
        syntax_errors.append("Error de sintaxis: falta la comilla doble '\"'.")

    # Comprobar las líneas esperadas
    for line in lines:
        stripped_line = line.strip()
        
        for expected_line in expected_structure:
            if stripped_line == expected_line.strip() or stripped_line == expected_line.rstrip(';'):
                found_lines[expected_line] = True

    # Comprobar si falta alguna línea esperada
    for expected_line, found in found_lines.items():
        if not found:
            syntax_errors.append(f"Error de sintaxis: falta '{expected_line}'.")

    # Verificar si hay líneas adicionales no esperadas
    for line in lines:
        stripped_line = line.strip()
        if stripped_line and not any(
            stripped_line == expected_line or stripped_line == expected_line.rstrip(';')
            for expected_line in expected_structure
        ):
            syntax_errors.append(f"Error de sintaxis: línea inesperada '{stripped_line}'.")

    # Si hay errores, los retornamos
    if syntax_errors:
        return render_template('index.html', lexical_results=None, syntactic_result=None, syntax_errors='; '.join(syntax_errors), counters=None, code=text)

    # Si no hay errores, establecer el resultado sintáctico correcto
    syntactic_result = "Resultado Sintáctico Correcto"

    return render_template('index.html', lexical_results=None, syntactic_result=syntactic_result, syntax_errors=None, counters=None, code=text)

@app.route('/clear', methods=['POST'])
def clear():
    return render_template('index.html', code='')

if __name__ == '__main__':
    app.run(debug=True)
