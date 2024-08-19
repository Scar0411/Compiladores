#mi primer analizador lexico que solo me reconocer 
# numeros enteros, identificadores, operadores
# librerias: lexico, re

import re

#crear tokens
token_patterns = [
    ('NUMERO', r'\d+'),                      # Número entero
    ('IDENTIFICADOR', r'[A-Za-z]\w*'),       # Identificador
    ('SUMA', r'\+'),                         # Operador de suma
    ('RESTA', r'-'),                         # Operador de resta
    ('MULTIPLICACION', r'\*'),               # Operador de multiplicación
    ('DIVISION', r'/'),                      # Operador de división
    ('PARENTESIS_IZQ', r'\('),               # Paréntesis izquierdo
    ('PARENTESIS_DER', r'\)'),               # Paréntesis derecho
    ('ESPACIO', r'\s+'),                     # Espacios
    ('SIMBOLO', r'.'),                          # Otros caracteres

]

# token expresiones regulares patrones
token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_patterns)
get_token = re.compile(token_regex).match

def tokenize(code):
    line_number = 1
    line_start = 0
    position = 0
    tokens = []

    while position < len(code):
        match = get_token(code, position)
        if not match:
            raise RuntimeError(f'Error de Analisis en posicion {position}')
        
        for name, value in match.groupdict().items():
            if value:
                if name != 'ESPACIO':
                    tokens.append((name, value))
                break
        position = match.end()

    return tokens  # Mover el return fuera del bucle while



code = "x = 2 + 4 * (2 - 8)"
tokens = tokenize(code)
for token in tokens:
    print(token) 