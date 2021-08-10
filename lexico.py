##########################################################################################################
# Nesse arquivo estamos construindo o analisador léxico, ele quebra nosso código caractere a caractere   #
# numa tentaiva de associar cada palavra do código a tokens. Um token está sempre associado a um tipo e, #
# opcionalmente, a um valor. A representação dos token costuma ser simples e clara.                      #
##########################################################################################################

#############################
## Definição de Constantes ##
#############################

digitos = '0123456789'

#####################
## Definição Erros ##
#####################

class Erro:

    # Inicializador da classe
    def __init__(self, nome_erro, detalhes):
        self.nome_erro = nome_erro
        self.detalhes = detalhes
    
    # Mensagem de retorno do erro
    def str_retorno(self):
        self.msg_erro = f'{self.nome_erro}: {self.detalhes}'

class ErroCharIlegal(Erro):

    # Inicializador do erro char ilegal
    def __init__(self, detalhes):
        super().__init__("Caractere Ilegal", detalhes)

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

class Token:

    # Inicializador da classe
    def __init__(self, tipo, valor=''):
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
    def cria_tokens(self):
        tokens = []
        # Loop que passa por cada caractere
        while self.char_atual != None:
            if self.char_atual in " \t":
                self.avan()
            elif self.char_atual in digitos:
                tokens.append(self.cria_num())
            elif self.char_atual == '+':
                tokens.append(Token(T_PLUS))
            elif self.char_atual == '-':
                tokens.append(Token(T_MINUS))
            elif self.char_atual == '*':
                tokens.append(Token(T_MULT))
            elif self.char_atual == '/':
                tokens.append(Token(T_DIV))
            elif self.char_atual == '(':
                tokens.append(Token(T_LPAREN))
            elif self.char_atual == ')':
                tokens.append(Token(T_MINUS))
            else:
                char = self.char_atual
                self.avan()
                return [], ErroCharIlegal(f'Erro no char {char}')
        return tokens, None

    # Método que define se o número é válido e qual seu formato            
    def cria_num(self):
        str_num = ''
        pontos = 0
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
            return Token(T_INT, int(str_num))
        else:
            return Token(T_FLOAT, float(str_num))

#########################
## Função de Interface ##
#########################    

# Método usado como interface para outros módulos usados ao longo do projeto
def interface(texto):
    lexer = Lexico(texto)
    tokens, erro = lexer.cria_tokens()

    return tokens, erro