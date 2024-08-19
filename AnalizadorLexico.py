
#Analizador lexico 50 Tokens
#Oscar Abel Torres Gomez
#6-M

import re

# Crear tokens
token_patterns = [
    ('NUMERO', r'\d+(\.\d*)?'),                      # Número entero o decimal
    ('IDENTIFICADOR', r'[A-Za-z_]\w*'),              # Identificador
    ('SUMA', r'\+'),                                 # Operador de suma
    ('RESTA', r'-'),                                 # Operador de resta
    ('MULTIPLICACION', r'\*'),                       # Operador de multiplicación
    ('DIVISION', r'/'),                              # Operador de división
    ('POTENCIA', r'\^'),                             # Operador de potencia
    ('MODULO', r'%'),                                # Operador de módulo
    ('PARENTESIS_IZQ', r'\('),                       # Paréntesis izquierdo
    ('PARENTESIS_DER', r'\)'),                       # Paréntesis derecho
    ('CORCHETE_IZQ', r'\['),                         # Corchete izquierdo
    ('CORCHETE_DER', r'\]'),                         # Corchete derecho
    ('LLAVE_IZQ', r'\{'),                            # Llave izquierda
    ('LLAVE_DER', r'\}'),                            # Llave derecha
    ('COMA', r','),                                  # Coma
    ('PUNTO_Y_COMA', r';'),                          # Punto y coma
    ('DOS_PUNTOS', r':'),                            # Dos puntos
    ('PUNTO', r'\.'),                                # Punto
    ('IGUAL', r'='),                                 # Operador de asignación
    ('MENOR_QUE', r'<'),                             # Operador menor que
    ('MAYOR_QUE', r'>'),                             # Operador mayor que
    ('MENOR_IGUAL', r'<='),                          # Operador menor o igual que
    ('MAYOR_IGUAL', r'>='),                          # Operador mayor o igual que
    ('DIFERENTE', r'!='),                            # Operador diferente
    ('IGUAL_IGUAL', r'=='),                          # Operador igual
    ('AND', r'and'),                                 # Operador lógico AND
    ('OR', r'or'),                                   # Operador lógico OR
    ('NOT', r'not'),                                 # Operador lógico NOT
    ('ASIGNACION_ADICION', r'\+='),                  # Operador de asignación adición
    ('ASIGNACION_RESTA', r'-='),                     # Operador de asignación resta
    ('ASIGNACION_MULTIPLICACION', r'\*='),           # Operador de asignación multiplicación
    ('ASIGNACION_DIVISION', r'/='),                  # Operador de asignación división
    ('ASIGNACION_MODULO', r'%='),                    # Operador de asignación módulo
    ('ASIGNACION_POTENCIA', r'\^='),                 # Operador de asignación potencia
    ('COMENTARIO', r'\#.*'),                         # Comentario
    ('CADENA', r'\".*?\"|\'[^\']*\''),               # Cadena
    ('BOOLEANO', r'\b(True|False)\b'),               # Booleano
    ('NULO', r'\b(None)\b'),                         # Nulo
    ('ESPACIO', r'\s+'),                             # Espacio
    ('SALTO_LINEA', r'\n'),                          # Salto de línea
    ('TABULACION', r'\t'),                           # Tabulación
    ('ARROBA', r'@'),                                # Decorador
    ('BACKSLASH', r'\\'),                            # Backslash
    ('BARRA_VERTICAL', r'\|'),                       # Barra vertical
    ('DOS_PUNTOS_IGUAL', r'::'),                     # Dos puntos seguidos
    ('TILDE', r'~'),                                 # Tilde
    ('CIRCUNFLEXO', r'\^'),                          # Circunflejo
    ('DOLAR', r'\$'),                                # Dólar
    ('ASTERISCO_DOS_PUNTOS', r'\*:'),                # Asterisco seguido de dos puntos
    ('DOS_PUNTOS_DOBLE', r'::'),                     # Dos puntos seguidos
]

# token expresiones regulares patrones
token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_patterns)
get_token = re.compile(token_regex).match

def tokenize(code):
    line_number = 1
    line_start = 0
    position = 0
    tokens = []
    token_count = 0  # Contador de tokens

    while position < len(code):
        match = get_token(code, position)
        if not match:
            raise RuntimeError(f'Error de Analisis en posicion {position}')
        
        for name, value in match.groupdict().items():
            if value:
                if name != 'ESPACIO':
                    tokens.append((name, value))
                    token_count += 1  # Incrementa el contador de tokens
                break
        position = match.end()

    return tokens

code = "f(x) = (2x^2 - 3x + 1) / (x - 2)"
tokens = tokenize(code)

# Imprimir los tokens con un contador
for i, token in enumerate(tokens, start=1):
    print(f"{i}: {token}")
    