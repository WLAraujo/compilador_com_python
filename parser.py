########################################################################################################################################################################################################
# Nesse arquivo desenvolveremos o parser da nossa linguagem. A ideia do parser é construir uma árvore de tokens que relacione os tokens de maneira sintática, ou seja, que dê sentido às relações      #
# dos tokens. Por exemplo, 123 456 ++ não faz sentido em nossa linguagem, mas 123 + 456 faz, esse é o objetivo do parser identificar o que faz e o que não faz sentido. Para começar a desenvolver um  #
# parser temos que primeiro definir as regras gramaticais da nossa linguagem. As regras gramaticais do nosso parser são definidas no gramatica.txt.                                                     #
########################################################################################################################################################################################################

import lexico
import erros

##################
## Tipos de Nós ## 
##################

class NoNumero:

    # Construtor do nó número será feito com base no próprio token que já indica se é int ou float
    def __init__(self, token):
        self.token = token
        self.pos_com = self.token.pos_com

    # Representação do nó
    def __rep__(self):
        return self.token.__rep__()

class NoOpBinaria:

    # Construtor do nó de operação binária
    def __init__(self, no_esq, token, no_dir):
        self.no_esq = no_esq
        self.token = token
        self.no_dir = no_dir
        self.pos_com = self.no_esq.pos_com

    def __rep__(self):
        return f'({self.no_esq.__rep__()}, {self.token.__rep__()}, {self.no_dir.__rep__()})'

class NoOpUnaria:

    # Método construtor da classe
    def __init__(self, token_op, no):
        self.token_op = token_op
        self.no = no
        self.pos_com = self.token_op.pos_com

    # Método de representação da operação
    def __rep__(self):
        return f'{self.token_op.__rep__()}, {self.no.__rep__()}'

#######################
## Criação do Parser ##
#######################

class Parser:

    # No construtor do parser temos que manter conhecimento sobre o token atualmente considerado e analisado
    def __init__(self, tokens):
        self.tokens = tokens
        self.token_index = -1
        self.avanc()

    # Método responsável por ir navegando entre os tokens passados
    def avanc(self):
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.token_atual = self.tokens[self.token_index]
        return self.token_atual

    # Método que inicia a realização do Parser
    def realizar_parse(self):
        resultado = self.expressao()
        if not resultado.erro and self.token_atual.tipo != lexico.T_EOF:
            return resultado.falha(erros.ErroSintaxeInvalida("Esperado algum operador"), self.token_atual.pos_com)
        return resultado

    # Criação de unidade
    def unidade(self):
        resultado = ResultadoParser()
        token = self.token_atual

        if token.tipo in (lexico.T_INT, lexico.T_FLOAT):
            resultado.registro(self.avanc())
            return resultado.sucesso(NoNumero(token))

        elif token.tipo == lexico.T_LPAREN:
            resultado.registro(self.avanc())
            expressao = resultado.registro(self.expressao())
            if resultado.erro:
                return resultado
            if self.token_atual.tipo == lexico.T_RPAREN:
                resultado.registro(self.avanc())
                return resultado.sucesso(expressao)
            else:
                return resultado.falha(erros.ErroSintaxeInvalida("Um ')' era esperado", self.token_atual.pos_com))

        return resultado.falha(erros.ErroSintaxeInvalida("Um valor int, float, +, - ou ( era esperado", self.token_atual.pos_com))

    # Criação de potência
    def potencia(self):
        return self.op_bin(self.unidade, (lexico.T_POW, ), self.fator)

    # Criação de fatores
    def fator(self):
        resultado = ResultadoParser()
        token = self.token_atual

        if token.tipo in (lexico.T_PLUS, lexico.T_MINUS):
            resultado.registro(self.avanc())
            # Criação de fator associado à op unária
            fator = resultado.registro(self.fator())
            if resultado.erro:
                return resultado
            return resultado.sucesso(NoOpUnaria(token, fator))

        return self.potencia()

    # Criação de termos
    def termo(self):
        return self.op_bin(self.potencia, (lexico.T_DIV, lexico.T_MULT))

    # Criação de expressões
    def expressao(self):
        return self.op_bin(self.termo, (lexico.T_PLUS, lexico.T_MINUS))

    # Método usado para reaproveitar código de termos e expressões que nada mais são que operações binárias
    def op_bin(self, funcao_a, operacoes, funcao_b = None):
        if funcao_b == None:
            funcao_b = funcao_a
        resultado = ResultadoParser()
        esquerda = resultado.registro(funcao_a())
        if resultado.erro:
            return resultado
        while self.token_atual.tipo in operacoes:
            token_operacao = self.token_atual
            resultado.registro(self.avanc())
            direita = resultado.registro(funcao_b())
            if resultado.erro:
                return resultado
            esquerda = NoOpBinaria(esquerda, token_operacao, direita)
        return resultado.sucesso(esquerda)

####################################
## Classe de Resultados do Parser ##
####################################

# Classe que mantém vigilância se ocorreu um erro no processo de parse e é responsável por devolver os resultados do processo
class ResultadoParser:

    # Construtor da classe
    def __init__(self):
        self.erro = None
        self.no = None
    
    # Método que devolve o resultado do processo de parse
    def registro(self, resultado):
        if isinstance(resultado, ResultadoParser):
            if resultado.erro: 
                self.erro = resultado.erro
            return resultado.no
        return resultado

    # Caso tenhamos sucesso no processo devolvemos o nó
    def sucesso(self, no):
        self.no = no
        return self

    # Caso tenhamos fracasso no processo devolvemos o erro
    def falha(self, erro):
        self.erro = erro
        return self

#########################
## Função de Interface ##
#########################   

# A interface do parser
def interface(tokens):
    parser = Parser(tokens)
    arv_parser = parser.realizar_parse()
    return arv_parser.no, arv_parser.erro