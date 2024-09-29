from flask import Flask, request, render_template
import ply.lex as lex
import ply.yacc as yacc

app = Flask(__name__)

# Lista global para almacenar los resultados de los tokens y del análisis sintáctico
resultado_lexema = []
resultado_sintactico = []
palabras_reservadas = 0

# Diccionario para almacenar el estado de inicialización de variables
variables_inicializadas = {}

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
    'igual', 'menorigual', 'mayorigual', 'menor', 'mayor', 'entero', 'cadena', 'punto', 'puntoycoma', 'incremento'
]

# Expresiones regulares para tokens simples
t_PARIZQ = r'\('
t_PARDER = r'\)'
t_LLAIZQ = r'\{'
t_LLADER = r'\}'
t_igual = r'='
t_menorigual = r'<='
t_mayorigual = r'>='
t_menor = r'<'
t_mayor = r'>'
t_suma = r'\+'
t_incremento = r'\+\+'
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
    '''for_loop : FOR PARIZQ variable_declaracion puntoycoma condicion puntoycoma incremento_statement PARDER LLAIZQ statement LLADER'''
    p[0] = "Bucle for correctamente estructurado"

# Modificar la función de declaración de variables
def p_variable_declaracion(p):
    '''variable_declaracion : INT identificador igual entero'''
    variables_inicializadas[p[2]] = True  # Marcar la variable como inicializada
    p[0] = f"Declaración válida de variable '{p[2]} = {p[4]}'"

# Detectar un error en la declaración de la variable (por ejemplo, 'int 1 = 1')
def p_variable_declaracion_error(p):
    '''variable_declaracion_error : INT error igual entero'''
    global resultado_sintactico
    resultado_sintactico.append("Error: el identificador no es válido. No puede comenzar con un número o tener caracteres inválidos.")
    p[0] = None  # Para indicar que hubo un error y no seguir procesando esta regla

# Definir la regla para manejar correctamente el incremento 'i++'
def p_incremento_statement(p):
    '''incremento_statement : identificador incremento'''
    p[0] = f"Incremento válido '{p[1]}++'"

# Modificar la regla de condición para verificar la inicialización de variables y la sintaxis
def p_condicion(p):
    '''condicion : identificador operador_comparacion entero
                 | condicion_error'''
    if p[1] not in variables_inicializadas or not variables_inicializadas[p[1]]:
        global resultado_sintactico
        resultado_sintactico.append(f"Error: la variable '{p[1]}' no ha sido inicializada antes de su uso.")
    else:
        # Verificación adicional para prevenir ciclos infinitos
        if p[2] == '!=' and p[3] == 5 and p[1] == 'i':  # Suponiendo que 'i' es la variable del bucle
            resultado_sintactico.append("Advertencia: posible ciclo infinito en el bucle for con condición 'i != 5'.")
        p[0] = f"Condición válida: '{p[1]} {p[2]} {p[3]}'"

# Detectar el error en la condición faltante el operador
def p_condicion_error(p):
    '''condicion_error : identificador entero'''
    global resultado_sintactico
    resultado_sintactico.append("Error: falta un operador de comparación en la condición del ciclo for.")
    p[0] = None

# Definir los operadores de comparación permitidos
def p_operador_comparacion(p):
    '''operador_comparacion : menor
                            | mayor
                            | menorigual
                            | mayorigual
                            | igual'''
    p[0] = p[1]

# Agregar una regla para detectar condiciones incompletas
def p_condicion_incompleta(p):
    '''condicion : identificador operador_comparacion error'''
    global resultado_sintactico
    resultado_sintactico.append("Error: condición incompleta. Debe incluir una comparación válida.")
    p[0] = None

# Modificar la regla statement para manejar las llaves
def p_statement(p):
    '''statement : SYSTEMOUT PARIZQ cadena suma identificador PARDER puntoycoma
                 | error_missing_closing_brace'''
    p[0] = "Impresión con System.out.println"

# Definir un error para el caso de que falte la llave de cierre '}'
def p_error_missing_closing_brace(p):
    '''error_missing_closing_brace : LLAIZQ statement'''
    global resultado_sintactico
    resultado_sintactico.append("Error: falta la llave de cierre '}'")
    p[0] = None

# Capturar errores sintácticos
def p_error(p):
    global resultado_sintactico
    resultado_sintactico.clear()  # Limpiar los resultados anteriores
    if p:
        resultado_sintactico.append(f"Error sintáctico: '{p.value}' en la línea {p.lineno}")
    else:
        resultado_sintactico.append("Error sintáctico: Se encontró un fin de archivo inesperado (EOF), posiblemente falta una llave de cierre '}'.")

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
