##########################################################################################################
# Nesse arquivo estamos construindo o analisador léxico, ele quebra nosso código caractere a caractere   #
# numa tentaiva de associar cada palavra do código a tokens. Um token está sempre associado a um tipo e, #
# opcionalmente, a um valor. A representação dos token costuma ser simples e clara.                      #
##########################################################################################################

##########################
## Definição dos Tokens ##
##########################

T_INT = "INT"
T_FLOAT = "FLOAT"
T_PLUS = "PLUS"
T_MINUS = "MINUS"
T_DIV = "DIV"
T_LPAREN = "LPAREN"
T_RPAREN = "RPAREN"

class Token:

    # Inicializador da classe
    def __init__(self, tipo, valor):
        self.tipo = tipo
        self.valor = valor

    # Método para representação em conjunto com o token
    def __rep__(self):
        if self.valor:
            return f'{self.tipo}:{self.valor} '

####################################
## Definição do Analisador Léxico ##
####################################

class Lexico:

    # Inicializador da classe
    def __init__(self, texto):
        self.texto = texto
        self.pos = -1 # mantém atualizada a posição atual
        self.char_atual = None # guarda o caractere atualmente atualizado
        self.avan()

    # Avança para a próxima posição do texto
    def avan(self):
        self.pos += 1
        self.char_atual = self.texto[self.pos] if self.pos <len(self.texto) else None

    # Método que associa os tokens
    #def cria_token(self):
    #    tokens = []

    #    whi
