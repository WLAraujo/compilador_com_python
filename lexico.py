##########################################################################################################
# Nesse arquivo estamos construindo o analisador léxico, ele quebra nosso código caractere a caractere   #
# numa tentaiva de associar cada palavra do código a tokens. Um token está sempre associado a um tipo e, #
# opcionalmente, a um valor. A representação dos token costuma ser simples e clara.                      #
##########################################################################################################

import erros

#############################
## Definição de Constantes ##
#############################

digitos = '0123456789'

##################################
## Posição do Analisador Léxico ##
##################################

# Nessa classe pretendemos manter o rastro da posição em que o nosso analisador léxico está, assim podemos identificar onde está o erro
class Position:

    # Construtor da classe que caracteriza uma posição
    def __init__(self, index, lin, col, nome_arq, texto_arq):
        self.index = index
        self.col = col
        self.lin = lin
        self.nome_arq = nome_arq
        self.texto_arq = texto_arq

    # Método que avança para a próxima linha e coluna
    def avanc(self, char_atual = None):
        self.index += 1
        self.col += 1
        if char_atual == '\n':
            self.lin += 1
            self.col = 0
        return self
    
    # Método que retorna a posição atual
    def copia(self):
        return Position(self.index, self.lin, self.col, self.nome_arq, self.texto_arq)

##########################
## Definição dos Tokens ##
##########################

T_INT = "INT"
T_FLOAT = "FLOAT"
T_PLUS = "PLUS"
T_MINUS = "MINUS"
T_DIV = "DIV"
T_MULT = "MULT"
T_LPAREN = "LPAREN"
T_RPAREN = "RPAREN"
T_EOF = 'EOF'

class Token:

    # Inicializador da classe
    def __init__(self, tipo, valor='', pos_com = None, pos_fim = None):
        self.tipo = tipo
        self.valor = valor
        if pos_com:
            self.pos_com = pos_com.copia()
            self.pos_fim = pos_com.copia()
            self.pos_fim.avanc()
        if pos_fim:
            self.pos_fim = pos_fim.copia()

    # Método para representação em conjunto com o token
    def __rep__(self):
        if self.valor:
            return f'{self.tipo}:{self.valor} '
        else:
            return f'{self.tipo} '

####################################
## Definição do Analisador Léxico ##
####################################

class Lexico:

    # Inicializador da classe
    def __init__(self, texto, nome_arq):
        self.texto = texto
        self.pos = Position(-1, 0, -1, nome_arq, texto) # mantém atualizada a posição atual
        self.char_atual = None # guarda o caractere atualmente atualizado
        self.nome_arq = nome_arq
        self.avan()
        

    # Avança para a próxima posição do texto
    def avan(self):
        self.pos.avanc(self.char_atual)
        self.char_atual = self.texto[self.pos.index] if self.pos.index < len(self.texto) else None

    # Método que associa os tokens
    def cria_tokens(self):
        tokens = []
        # Loop que passa por cada caractere
        while self.char_atual != None:
            if self.char_atual in " \t":
                self.avan()
            elif self.char_atual in digitos:
                tokens.append(self.cria_num())
            elif self.char_atual == '+':
                tokens.append(Token(T_PLUS, pos_com=self.pos))
                self.avan()
            elif self.char_atual == '-':
                tokens.append(Token(T_MINUS, pos_com=self.pos))
                self.avan()
            elif self.char_atual == '*':
                tokens.append(Token(T_MULT, pos_com=self.pos))
                self.avan()
            elif self.char_atual == '/':
                tokens.append(Token(T_DIV, pos_com=self.pos))
                self.avan()
            elif self.char_atual == '(':
                tokens.append(Token(T_LPAREN, pos_com=self.pos))
                self.avan()
            elif self.char_atual == ')':
                tokens.append(Token(T_RPAREN, pos_com=self.pos))
                self.avan()
            else:
                pos_inicio = self.pos.copia()
                char = self.char_atual
                self.avan()
                return [], erros.ErroCharIlegal(f'Erro no caractere {char}', pos_inicio = pos_inicio)
        tokens.append(Token(T_EOF, pos_com=self.pos))
        return tokens, None

    # Método que define se o número é válido e qual seu formato            
    def cria_num(self):
        str_num = ''
        pontos = 0
        pos_com = self.pos.copia()
        while self.char_atual != None and self.char_atual in digitos + '.':
            if self.char_atual == '.':
                if pontos == 1:
                    break
                pontos += 1
                str_num += '.'
            else:
                str_num += self.char_atual
            self.avan()
        if pontos == 0:
            return Token(T_INT, int(str_num), pos_com)
        else:
            return Token(T_FLOAT, float(str_num), pos_com)

#########################
## Função de Interface ##
#########################    

# Método usado como interface para outros módulos usados ao longo do projeto, no caso do analisador léxico vamos criar os tokens com o método abaixo
def interface(texto, nome_arq):
    lexer = Lexico(texto, nome_arq)
    tokens, erro = lexer.cria_tokens()
    return tokens, erro