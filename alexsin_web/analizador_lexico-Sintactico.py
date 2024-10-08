from flask import Flask, render_template, request, redirect, url_for
import ply.lex as lex
import ply.yacc as yacc
import re

app = Flask(__name__)

# Definición de tokens para el analizador léxico
tokens = (
    'ID', 'NUMBER', 'STRING', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 
    'IF', 'ELSE', 'WHILE', 'FOR', 'EQUALS', 'LPAREN', 'RPAREN', 
    'LBRACE', 'RBRACE', 'COMMA', 'SEMICOLON', 'QUOTE', 'INT', 
    'READ', 'PRINT', 'END'
)

# Definición de los nuevos símbolos
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_COMMA = r','
t_SEMICOLON = r';'
t_QUOTE = r'\"'

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_EQUALS = r'='

# Palabras reservadas
reserved = {
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'for': 'FOR',
    'int': 'INT',
    'read': 'READ',
    'printf': 'PRINT',
    'end': 'END'
}

# Reglas simples de tokens
t_ignore = ' \t'

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')  # Check for reserved words
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING(t):
    r'\"([^\\\n]|(\\.))*?\"'
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count('\n')

def t_error(t):
    print(f"Carácter ilegal '{t.value[0]}' en línea {t.lexer.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()

# Analizador sintáctico
def p_program(p):
    '''program : ID LBRACE declarations statements END'''
    pass

def p_declarations(p):
    '''declarations : type ID COMMA ID COMMA ID SEMICOLON
                    | type ID SEMICOLON'''
    pass

def p_type(p):
    '''type : INT'''
    pass

def p_statements(p):
    '''statements : statement statements
                  | statement'''
    pass

def p_statement_read(p):
    '''statement : READ ID SEMICOLON'''
    pass

def p_statement_assign(p):
    '''statement : ID EQUALS expression SEMICOLON'''
    pass

def p_statement_print(p):
    '''statement : PRINT LPAREN STRING RPAREN SEMICOLON'''
    pass

def p_expression_binop(p):
    '''expression : ID PLUS ID
                  | ID MINUS ID
                  | ID TIMES ID
                  | ID DIVIDE ID'''
    pass

def p_error(p):
    if p:
        error_msg = f"Error de sintaxis en '{p.value}' en la línea {p.lineno}. "
        if p.type in ['ID', 'INT', 'READ', 'PRINT', 'END']:
            error_msg += f"Se esperaba un símbolo o palabra reservada."
        else:
            error_msg += f"Token inesperado."
        print(error_msg)  # Para depuración en la consola
        return error_msg
    else:
        return "Error de sintaxis al final del archivo. Verifica que todos los bloques están correctamente cerrados."

parser = yacc.yacc()

@app.route('/')
def index():
    return render_template('index.html', lexical_results=None, syntactic_result=None, syntax_errors=None, counters=None, code='')

@app.route('/lexical', methods=['POST'])
def lexical_analysis():
    text = request.form['code']
    lexer.lineno = 1  # Reiniciar la cuenta de líneas
    lexer.input(text)
    lexical_results = []
    
    # Contadores para los tipos de tokens
    counters = {
        'Reservada': 0,
        'Identificador': 0,
        'Cadena': 0,
        'Numero': 0,
        'Simbolo': 0,
        'Total': 0
    }

    while True:
        tok = lexer.token()
        if not tok:
            break
        token_info = {
            'linea': tok.lineno,
            'token': tok.value,
            'pr': 'X' if tok.type in ['IF', 'ELSE', 'WHILE', 'FOR', 'INT', 'READ', 'PRINT', 'END'] else '',
            'id': 'X' if tok.type == 'ID' else '',
            'cad': 'X' if tok.type == 'STRING' else '',
            'num': 'X' if tok.type == 'NUMBER' else '',
            'simbolo': 'X' if tok.type in ['PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'COMMA', 'SEMICOLON', 'QUOTE'] else '',
            'tipo': {
                'ID': 'Identificador','NUMBER': 'Número','STRING': 'Cadena','PLUS': 'Suma','MINUS': 'Resta','TIMES': 'Multiplicación',
                'DIVIDE': 'División','IF': 'Si','ELSE': 'Sino','WHILE': 'Mientras','FOR': 'Para','EQUALS': 'Igual','LPAREN': 'Paréntesis Izquierdo',
                'RPAREN': 'Paréntesis Derecho','LBRACE': 'Llave Izquierda','RBRACE': 'Llave Derecha','COMMA': 'Coma','SEMICOLON': 'Punto y Coma',
                'QUOTE': 'Comillas','INT': 'Entero','READ': 'Leer','PRINT': 'Imprimir','END': 'Fin'
            }[tok.type]  # Cambiar a español aquí
        }
        lexical_results.append(token_info)

        # Incrementamos el contador según el tipo de token
        if token_info['pr'] == 'X':
            counters['Reservada'] += 1
        if token_info['id'] == 'X':
            counters['Identificador'] += 1
        if token_info['cad'] == 'X':
            counters['Cadena'] += 1
        if token_info['num'] == 'X':
            counters['Numero'] += 1
        if token_info['simbolo'] == 'X':
            counters['Simbolo'] += 1

        counters['Total'] += 1

    return render_template('index.html', lexical_results=lexical_results, syntactic_result=None, syntax_errors=None, counters=counters, code=text)

@app.route('/syntactic', methods=['POST'])
def syntactic_analysis():
    text = request.form['code']
    lines = text.splitlines()  # Dividir el código en líneas
    syntax_errors = []
    declared_variables = set()
    int_declared = False
    expected_variables = {'a', 'b', 'c'}
    end_present = False  # Variable para verificar si 'end' está presente
    program_present = False  # Verificar si 'program' está presente
    suma_present = False  # Verificar si 'suma' está presente

    # 1. Verificar la llave de inicio '{' solo en la primera línea
    if lines and '{' not in lines[0]:
        syntax_errors.append("Error de sintaxis: Falta la llave de inicio '{' al inicio del bloque.")

    # 2. Verificar la llave de cierre '}' solo en la última línea
    if lines and '}' not in lines[-1]:
        syntax_errors.append("Error de sintaxis: Falta la llave de cierre '}' al final del bloque.")

    # Si hay errores, los retornamos sin intentar el análisis sintáctico
    if syntax_errors:
        return render_template('index.html', lexical_results=None, syntactic_result=None, syntax_errors='; '.join(syntax_errors), counters=None, code=text)

    # Recorrer las líneas de código para otros errores
    for i, line in enumerate(lines):
        # Comprobar si la palabra 'end' está presente
        if 'end' in line:
            end_present = True

        # Comprobar si 'program' está presente
        if 'program' in line:
            program_present = True

        # Comprobar si 'suma' está presente
        if 'suma' in line:
            suma_present = True

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
                        syntax_errors.append(f"Error de sintaxis en la línea {i + 1}: Token inesperado '+'.")
                        break

        # Comprobar uso de variables no declaradas al asignar
        if '=' in line:
            right_side = line.split('=')[1]
            for variable in declared_variables:
                if variable not in right_side and variable != '1' and re.match(r'^\d+$', variable):
                    syntax_errors.append(f"Error: variable '{variable}' no definida en la línea {i + 1}.")

    # Verificar si faltan las variables 'a', 'b', 'c' en la declaración
    missing_variables = expected_variables - declared_variables
    for var in missing_variables:
        syntax_errors.append(f"Error de sintaxis: Variable no definida para '{var}'.")

    # Verificar si falta la palabra reservada 'int' o no ha sido declarada
    if not int_declared:  # Se asegura de verificar si 'int' fue declarado
        syntax_errors.append("Error: palabra reservada 'int' no declarada.")

    # Verificar si la palabra reservada 'end' falta
    if not end_present:
        syntax_errors.append("Error: sintaxis palabra reservada 'end' faltante.")

    # Verificar si falta el identificador 'program'
    if not program_present:
        syntax_errors.append("Error de sintaxis: identificador 'program' faltante.")

    # Verificar si falta el identificador 'suma'
    if not suma_present:
        syntax_errors.append("Error de sintaxis: identificador 'suma' faltante.")

    # Si no hay errores, establecer el resultado sintáctico correcto
    syntactic_result = None
    if not syntax_errors:
        syntactic_result = "Resultado Sintáctico Correcto"

    return render_template('index.html', lexical_results=None, syntactic_result=syntactic_result, syntax_errors='; '.join(syntax_errors), counters=None, code=text)

@app.route('/clear', methods=['POST'])
def clear():
    # Renderiza la página con todos los valores vacíos
    return render_template('index.html', lexical_results=None, syntactic_result=None, syntax_errors=None, counters=None, code='')

if __name__ == '__main__':
    app.run(debug=True)
