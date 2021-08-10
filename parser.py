########################################################################################################################################################################################################
# Nesse arquivo desenvolveremos o parser da nossa linguagem. A ideia do parser é construir uma árvore de tokens que relacione os tokens de maneira sintática, ou seja, que dê sentido às relações      #
# dos tokens. Por exemplo, 123 456 ++ não faz sentido em nossa linguagem, mas 123 + 456 faz, esse é o objetivo do parser identificar o que faz e o que não faz sentido. Para começar a desenvolver um  #
# parser temos que primeiro definir as regras gramaticais da nossa linguagem. As regras gramaticais do nosso parser são definidas no gramatica.txt.                                                     #
########################################################################################################################################################################################################

import lexico

##################
## Tipos de Nós ## 
##################

class NoNumero:

    # Construtor do nó número será feito com base no próprio token que já indica se é int ou float
    def __init__(self, token):
        self.token = token

    # Representação do nó
    def __rep__(self):
        return f'{self.token}'

class NoOpBinaria:

    # Construtor do nó de operação binária
    def __init__(self, no_esq, token, no_dir):
        self.no_esq = no_esq
        self.token = token
        self.no_dir = no_dir

    def __rep__(self):
        return f'{self.left_node}, {self.token}, {self.right_node}'

#######################
## Criação do Parser ##
#######################

class Parser:

    # No construtor do parser temos que manter conhecimento sobre o token atualmente considerado e analisado
    def __init__(self, tokens):
        self.tokens = tokens
        self.token_index = 1
        self.avanc()

    # Método responsável por ir navegando entre os tokens passados
    def avanc(self):
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.token_atual = self.tokens[self.token_index]
        return self.token_atual

    # Criação de fatores
    def fator(self):
        token = self.token_atual
        if token.tipo in (lexico.T_INT, lexico.T_FLOAT):
            self.avanc()
            return NoNumero(token)
    
    # Criação de termos
    def termo(self):
        return self.op_bin(self.fator, (lexico.T_DIV, lexico.T_MULT))

    # Criação de expressões
    def expressao(self):
        return self.op_bin(self.termo, (lexico.T_PLUS, lexico.T_MINUS))

    # Método usado para reaproveitar código de termos e expressões que nada mais são que operações binárias
    def op_bin(self, op_sobre, operacoes):
        esquerda = op_sobre()
        while self.token_atual.tipo in operacoes:
            token_operacao = self.token_atual
            self.avanc()
            direita = op_sobre()
            esquerda = NoOpBinaria(esquerda, token_operacao, direita)
        return esquerda

    def realizar_parse(self):
        resultado = self.expressao()
        return resultado

# A interface do parser
def interface(tokens):
    parser = Parser(tokens)
    arv_parser = parser.realizar_parse()
    return arv_parser