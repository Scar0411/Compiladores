from flask import Flask, request, render_template
import ply.lex as lex
import ply.yacc as yacc

app = Flask(__name__)

# Lista global para almacenar los resultados de los tokens y del análisis sintáctico
resultado_lexema = []
resultado_sintactico = []
palabras_reservadas = 0

# Palabras reservadas
reservada = {
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'for': 'FOR',
    'print': 'PRINT',
    'return': 'RETURN',
    'break': 'BREAK',
    'true': 'TRUE',
    'false': 'FALSE',
    'int': 'INT',
}

# Tokens
tokens = list(reservada.values()) + [
    'SYSTEMOUT', 'identificador', 'suma', 'PARIZQ', 'PARDER', 'LLAIZQ', 'LLADER',
    'igual', 'mayorigual', 'entero', 'cadena', 'punto', 'puntoycoma'
]

# Expresiones regulares para tokens simples
t_PARIZQ = r'\('
t_PARDER = r'\)'
t_LLAIZQ = r'\{'
t_LLADER = r'\}'
t_igual = r'='
t_mayorigual = r'<='
t_suma = r'\+'
t_punto = r'\.'
t_puntoycoma = r';'
t_cadena = r'\".*?\"'

# Definir la regla para reconocer System.out.println
def t_SYSTEMOUT(t):
    r'System\.out\.println'
    return t

# Definir la regla para los enteros
def t_entero(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Definir la regla para identificadores (incluye palabras reservadas)
def t_identificador(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reservada.get(t.value, 'identificador')  # Si es una palabra reservada, usa su token
    return t

# Ignorar espacios y tabulaciones
t_ignore = ' \t'

# Manejar errores de tokens
def t_error(t):
    global resultado_lexema
    estado = "Token no Válido"
    resultado_lexema.append({'token': 'ERROR', 'lexema': t.value, 'linea': t.lineno})
    t.lexer.skip(1)

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Función para probar la entrada con el analizador léxico
def prueba_lexico(data):
    global resultado_lexema, palabras_reservadas
    resultado_lexema.clear()  # Limpiar la lista antes de cada prueba
    palabras_reservadas = 0
    analizador = lex.lex()    # Crear el analizador léxico
    analizador.input(data)    # Cargar la entrada
    while True:
        tok = analizador.token()
        if not tok:
            break
        if tok.type in reservada.values() or tok.type == 'SYSTEMOUT':
            palabras_reservadas += 1
        resultado_lexema.append({'token': tok.type, 'lexema': tok.value, 'linea': tok.lineno})

# Funciones de análisis sintáctico
def p_for_loop(p):
    '''for_loop : FOR PARIZQ INT identificador igual entero puntoycoma identificador mayorigual entero puntoycoma identificador suma suma PARDER LLAIZQ statement LLADER'''
    p[0] = "Bucle for correctamente estructurado"

def p_statement(p):
    '''statement : SYSTEMOUT PARIZQ cadena suma identificador PARDER puntoycoma'''
    p[0] = "Impresión con System.out.println"

# Capturar errores sintácticos
def p_error(p):
    global resultado_sintactico
    resultado_sintactico.clear()  # Limpiar los resultados anteriores
    if p:
        resultado_sintactico.append(f"Error sintáctico: '{p.value}' en la línea {p.lineno}")
    else:
        resultado_sintactico.append("Error sintáctico: Se encontró un fin de archivo inesperado (EOF)")

# Función para probar la entrada con el analizador sintáctico
def prueba_sintactico(data):
    global resultado_sintactico
    resultado_sintactico.clear()  # Limpiar los resultados anteriores
    parser = yacc.yacc()  # Crear el analizador sintáctico
    try:
        parser.parse(data)  # Realizar el análisis
        if len(resultado_sintactico) == 0:
            resultado_sintactico.append("Código sintácticamente correcto")
    except Exception as e:
        resultado_sintactico.append(f"Error de análisis: {str(e)}")

# Ruta principal que muestra el formulario y el resultado
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.form['code']  # Obtener el código ingresado en el formulario
        prueba_lexico(data)  # Pasar el texto al analizador léxico
        prueba_sintactico(data)  # Pasar el texto al analizador sintáctico

        return render_template('index.html', code=data, results=resultado_lexema, reserved_count=palabras_reservadas, token_count=len(resultado_lexema), sintactico=resultado_sintactico)

    # Si es una solicitud GET, solo muestra el formulario vacío
    return render_template('index.html', code='', results=None, reserved_count=0, token_count=0, sintactico=None)

if __name__ == '__main__':
    app.run(debug=True)
