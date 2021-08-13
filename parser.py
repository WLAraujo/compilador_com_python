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

class NoAcessoVar:

    # Método construtor da classe
    def __init__(self, token_var):
        self.token_var = token_var
        self.pos_com = token_var.pos_com

class NoAtribuiVar:

    # Método construtor da classe
    def __init__(self, token_var, valor_no):
        self.valor_no = valor_no
        self.token_var = token_var
        self.pos_com = token_var.pos_com

class NoSe:

    # Método construtor da classe
    def __init__(self, casos, caso_senao):
        self.casos = casos
        self.caso_senao = caso_senao
        self.pos_com = self.casos[0][0].pos_com


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
        if resultado.erro and self.token_atual.tipo != lexico.T_EOF:
            return resultado.falha(erros.ErroSintaxeInvalida("Esperado algum operador", self.token_atual.pos_com))
        return resultado

    # Criação de expressões que usam SE, MAS_SE, SENAO e ENTAO
    def expr_cond(self):
        resultado = ResultadoParser()
        casos = []
        caso_senao = None
        if not self.token_atual.token_bate(lexico.T_KEYWORD, 'SE'):
            return resultado.falha(erros.ErroSintaxeInvalida('Era esperado um SE', self.token_atual.pos_com))
        resultado.registro_avanc()
        self.avanc()
        condicao = resultado.registro(self.expressao())
        if resultado.erro:
            return resultado
        if not self.token_atual.token_bate(lexico.T_KEYWORD, 'ENTAO'):
            return resultado.falha(erros.ErroSintaxeInvalida('Era esperado um ENTAO', self.token_atual.pos_com))
        resultado.registro_avanc()
        self.avanc()
        expressao = resultado.registro(self.expressao())
        if resultado.erro:
            return resultado
        casos.append((condicao, expressao))
        while self.token_atual.token_bate(lexico.T_KEYWORD, 'MAS_SE'):
            resultado.registro_avanc()
            self.avanc()
            condicao = resultado.registro(self.expressao())
            if resultado.erro:
                return resultado
            if not self.token_atual.token_bate(lexico.T_KEYWORD, 'ENTAO'):
                return resultado.falha(erros.ErroSintaxeInvalida('Era esperado um ENTAO', self.token_atual.pos_com))
            resultado.registro_avanc()
            self.avanc()
            expressao = resultado.registro(self.expressao())
            if resultado.erro:
                return resultado
            casos.append((condicao, expressao))
        if self.token_atual.token_bate(lexico.T_KEYWORD, 'SENAO'):
            resultado.registro_avanc()
            self.avanc()
            expressao = resultado.registro(self.expressao())
            if resultado.erro:
                return resultado
            caso_senao = expressao
        return resultado.sucesso(NoSe(casos, caso_senao))


    # Criação de unidade
    def unidade(self):
        resultado = ResultadoParser()
        token = self.token_atual

        if token.tipo in (lexico.T_INT, lexico.T_FLOAT):
            resultado.registro_avanc() 
            self.avanc()
            return resultado.sucesso(NoNumero(token))

        elif token.tipo == lexico.T_IDENTIFICADOR:
            resultado.registro_avanc() 
            self.avanc()
            return resultado.sucesso(NoAcessoVar(token))

        elif token.tipo == lexico.T_LPAREN:
            resultado.registro_avanc() 
            self.avanc()
            expressao = resultado.registro(self.expressao())
            if resultado.erro:
                return resultado
            if self.token_atual.tipo == lexico.T_RPAREN:
                resultado.registro_avanc() 
                self.avanc()
                return resultado.sucesso(expressao)
            else:
                return resultado.falha(erros.ErroSintaxeInvalida("Um ')' era esperado", self.token_atual.pos_com))
        
        elif token.token_bate(lexico.T_KEYWORD, 'SE'):
            expr_se = resultado.registro(self.expr_cond())
            if resultado.erro:
                return resultado
            return resultado.sucesso(expr_se)

        return resultado.falha(erros.ErroSintaxeInvalida("Um valor int, float, identificador, 'VAR', '+', '-' ou '(' era esperado", self.token_atual.pos_com))

    # Criação de potência
    def potencia(self):
        return self.op_bin(self.unidade, (lexico.T_POW, ), self.fator)

    # Criação de fatores
    def fator(self):
        resultado = ResultadoParser()
        token = self.token_atual

        if token.tipo in (lexico.T_PLUS, lexico.T_MINUS):
            resultado.registro_avanc() 
            self.avanc()
            # Criação de fator associado à op unária
            fator = resultado.registro(self.fator())
            if resultado.erro:
                return resultado
            return resultado.sucesso(NoOpUnaria(token, fator))

        return self.potencia()

    # Criação de termos
    def termo(self):
        return self.op_bin(self.fator, (lexico.T_DIV, lexico.T_MULT))

    # Criação de expressões que envolvam comparações com os operadores <, >, <=, !=, >= e ==
    def expr_comp(self):
        resultado = ResultadoParser()
        if self.token_atual.token_bate(lexico.T_KEYWORD, 'NAO'):
            token_op = self.token_atual
            resultado.registro_avanc()
            self.avanc()
            no = resultado.registro(self.expr_comp())
            if resultado.erro:
                return resultado
            return resultado.sucesso(NoOpUnaria(token_op, no))
        
        no = resultado.registro(self.op_bin(self.expr_arit, (lexico.T_EHIGUAL, lexico.T_MAIORIGUALQ, lexico.T_MENORIGUALQ, lexico.T_MAIORQ, lexico.T_MENORQ, lexico.T_NIGUAL)))
        if resultado.erro:
            return resultado.falha(erros.ErroSintaxeInvalida("Um valor int, float, identificador, 'VAR', '+', '-', '(' ou 'NAO' era esperado", self.token_atual.pos_com))
        
        return resultado.sucesso(no)

    # Criação de expressões que envolvam operações aritméticas com fatores
    def expr_arit(self):
        return self.op_bin(self.termo, (lexico.T_PLUS, lexico.T_MINUS))

    # Criação de expressões
    def expressao(self):
        resultado = ResultadoParser()

        if self.token_atual.token_bate(lexico.T_KEYWORD, 'VAR'):
            resultado.registro_avanc() 
            self.avanc()
            if self.token_atual.tipo != lexico.T_IDENTIFICADOR:
                return resultado.falha(erros.ErroSintaxeInvalida('Era esperado um identificador', self.token_atual.pos_com))
            nome_variavel = self.token_atual

            resultado.registro_avanc() 
            self.avanc()
            if self.token_atual.tipo != lexico.T_EQ:
                return resultado.falha(erros.ErroSintaxeInvalida("Era esperado um atribuidor '='", self.token_atual.pos_com))
            
            resultado.registro_avanc() 
            self.avanc()
            expressao = resultado.registro(self.expressao())
            if resultado.erro:
                return resultado
            else:
                return resultado.sucesso(NoAtribuiVar(nome_variavel, expressao))

        no = resultado.registro(self.op_bin(self.expr_comp, ((lexico.T_KEYWORD, "E"), (lexico.T_KEYWORD, "OU"))))

        if resultado.erro:
            return resultado.falha(erros.ErroSintaxeInvalida("Um valor numerico, identificador, '+', '-' ou '(' era esperado", self.token_atual.pos_com))
        return resultado.sucesso(no)

    # Método usado para reaproveitar código de termos e expressões que nada mais são que operações binárias
    def op_bin(self, funcao_a, operacoes, funcao_b = None):
        if funcao_b == None:
            funcao_b = funcao_a
        resultado = ResultadoParser()
        if type(funcao_a) ==ResultadoParser:
            print(funcao_a.no)
        esquerda = resultado.registro(funcao_a())
        if resultado.erro:
            return resultado
        while self.token_atual.tipo in operacoes or (self.token_atual.tipo, self.token_atual.valor) in operacoes:
            token_operacao = self.token_atual
            resultado.registro_avanc() 
            self.avanc()
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
        self.cont_avancos = 0

    # Método que devolve o resultado do processo de parse
    def registro(self, resultado):
        self.cont_avancos += resultado.cont_avancos
        if resultado.erro: 
            self.erro = resultado.erro
        return resultado.no

    # Método de registro usado exclusivamente para avançar na análise
    def registro_avanc(self):
        self.cont_avancos += 1

    # Caso tenhamos sucesso no processo devolvemos o nó
    def sucesso(self, no):
        self.no = no
        return self

    # Caso tenhamos fracasso no processo devolvemos o erro
    def falha(self, erro):
        if not self.erro or self.cont_avancos == 0:
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