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

    def __init__(self, token_op, no):
        self.token_op = token_op
        self.no = no
        self.pos_com = token_op.pos_com

    # Método de representação da operação
    def __rep__(self):
        return f'{self.token_op.__rep__()}, {self.no.__rep__()}'

class NoAcessoVar:

    def __init__(self, token_var):
        self.token_var = token_var
        self.pos_com = token_var.pos_com

class NoAtribuiVar:

    def __init__(self, token_var, valor_no):
        self.valor_no = valor_no
        self.token_var = token_var
        self.pos_com = token_var.pos_com

class NoSe:

    def __init__(self, casos, caso_senao):
        self.casos = casos
        self.caso_senao = caso_senao
        self.pos_com = self.casos[0][0].pos_com

class NoPara:

    def __init__(self, token_var, valor_inicial, valor_final, valor_passo, no_corpo):
        self.token_var = token_var
        self.valor_inicial = valor_inicial
        self.valor_final = valor_final
        self.valor_passo = valor_passo
        self.no_corpo = no_corpo
        self.pos_com = self.token_var.pos_com

class NoEnquanto:

    def __init__(self, no_condicao, no_corpo):
        self.no_condicao = no_condicao
        self.no_corpo = no_corpo
        self.pos_com = self.no_condicao.pos_com

class NoDefFun:

    def __init__(self, token_nome_fun, tokens_fun_args, no_corpo):
        self.token_nome_fun = token_nome_fun
        self.tokens_fun_args = tokens_fun_args
        self.no_corpo = no_corpo
        if self.token_nome_fun:
            self.pos_com = self.token_nome_fun.pos_com
        elif len(self.tokens_fun_args) > 0:
            self.pos_com = self.tokens_fun_args[0].pos_com
        else:
        	self.pos_com = self.no_corpo.pos_com

class NoChamadaFun:

    def __init__(self, no_a_chamar, nos_args):
        self.no_a_chamar = no_a_chamar
        self.nos_args = nos_args
        self.pos_com = self.no_a_chamar.pos_com

class NoString:
    
    # Construtor do nó string
    def __init__(self, token):
        self.token = token
        self.pos_com = self.token.pos_com

    # Representação do nó
    def __rep__(self):
        return self.token.__rep__()

#######################
## Criação do Parser ##
#######################

# Cada método da classe Parser visa analisar uma regra sintática definida em nossa gramática

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

    # Criação de expressões que envolvam laço de iteração PARA
    def expr_para(self):
        resultado = ResultadoParser()

        if not self.token_atual.token_bate(lexico.T_KEYWORD, 'PARA'):
            return resultado.falha(erros.ErroSintaxeInvalida("Era esperado um 'PARA'", self.token_atual.pos_com))
        resultado.registro_avanc()
        self.avanc()

        if self.token_atual.tipo != lexico.T_IDENTIFICADOR:
            return resultado.falha(erros.ErroSintaxeInvalida("Era esperado um identificador de variável", self.token_atual.pos_com))
        nome_var = self.token_atual
        resultado.registro_avanc()
        self.avanc() 

        if self.token_atual.tipo != lexico.T_EQ:
            return resultado.falha(erros.ErroSintaxeInvalida("Era esperado um '='", self.token_atual.pos_com))
        resultado.registro_avanc()
        self.avanc() 

        valor_inicial = resultado.registro(self.expressao())
        if resultado.erro:
            return resultado

        if not self.token_atual.token_bate(lexico.T_KEYWORD, 'ATE'):
            return resultado.falha(erros.ErroSintaxeInvalida("Era esperado um 'ATE'", self.token_atual.pos_com))
        resultado.registro_avanc()
        self.avanc()

        valor_final = resultado.registro(self.expressao())
        if resultado.erro:
            return resultado

        if self.token_atual.token_bate(lexico.T_KEYWORD, 'C_PASSO'):
            resultado.registro_avanc()
            self.avanc()
            valor_passo = resultado.registro(self.expressao())
            if resultado.erro:
                return resultado
        else:
            valor_passo = None
        
        if not self.token_atual.token_bate(lexico.T_KEYWORD, 'REALIZE'):
            return resultado.falha(erros.ErroSintaxeInvalida("Era esperado um 'REALIZE'", self.token_atual.pos_com))
        resultado.registro_avanc()
        self.avanc()

        corpo = resultado.registro(self.expressao())
        if resultado.erro:
            return resultado

        return resultado.sucesso(NoPara(nome_var, valor_inicial, valor_final, valor_passo, corpo))

    # Criação de expressões que envolvam laço de iteração ENQUANTO
    def expr_enquanto(self):
        resultado = ResultadoParser()
        if not self.token_atual.token_bate(lexico.T_KEYWORD, 'ENQUANTO'):
            return resultado.falha(erros.ErroSintaxeInvalida("Era esperado um 'ENQUANTO'", self.token_atual.pos_com))
        resultado.registro_avanc()
        self.avanc()
        condicao = resultado.registro(self.expressao())
        if resultado.erro: 
            return resultado
        if not self.token_atual.token_bate(lexico.T_KEYWORD, 'REALIZE'):
            return resultado.falha(erros.ErroSintaxeInvalida("Era esperado um 'REALIZE", self.token_atual.pos_com))
        resultado.registro_avanc()
        self.avanc()
        corpo = resultado.registro(self.expressao())
        if resultado.erro: 
            return resultado
        return resultado.sucesso(NoEnquanto(condicao, corpo))

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

        if token.tipo == lexico.T_STRING:
            resultado.registro_avanc() 
            self.avanc()
            return resultado.sucesso(NoString(token))

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

        elif token.token_bate(lexico.T_KEYWORD, 'PARA'):
            expr_para = resultado.registro(self.expr_para())
            if resultado.erro:
                return resultado
            return resultado.sucesso(expr_para)
        
        elif token.token_bate(lexico.T_KEYWORD, 'ENQUANTO'):
            expr_enquanto = resultado.registro(self.expr_enquanto())
            if resultado.erro:
                return resultado
            return resultado.sucesso(expr_enquanto)

        elif token.token_bate(lexico.T_KEYWORD, 'FUN'):
            def_func = resultado.registro(self.func_def())
            if resultado.erro:
                return resultado
            return resultado.sucesso(def_func)

        return resultado.falha(erros.ErroSintaxeInvalida("Um valor int, float, identificador, 'VAR', '+', '-', '(', 'SE', 'ENQUANTO', 'PARA' ou 'FUN' era esperado", self.token_atual.pos_com))

    # Criação da chamada de funções
    def chamada(self):
        resultado = ResultadoParser()
        unidade = resultado.registro(self.unidade())
        if resultado.erro: 
            return resultado
        
        if self.token_atual.tipo == lexico.T_LPAREN:
            resultado.registro_avanc()
            self.avanc()

            nos_args = []

            if self.token_atual.tipo == lexico.T_RPAREN:
                resultado.registro_avanc()
                self.avanc()

            else:
                nos_args.append(resultado.registro(self.expressao()))
                if resultado.erro:
                    return resultado.failure(erros.ErroSintaxeInvalida("Esperado ')', 'VAR', 'SE', 'PARA', 'ENQUANTO', 'FUN', int, float, identificador, '+', '-', '(' ou 'NAO'", self.token_atual.pos_com))
                
                while self.token_atual.tipo == lexico.T_VIRG:
                    resultado.registro_avanc()
                    self.avanc()
                    nos_args.append(resultado.registro(self.expressao()))
                    if resultado.erro: 
                        return resultado

                if self.token_atual.tipo != lexico.T_RPAREN:
                    return resultado.failure(erros.ErroSintaxeInvalida("Esperado ',' ou ')'", self.token_atual.pos_com))

                resultado.registro_avanc()
                self.avanc()
            return resultado.sucesso(NoChamadaFun(unidade, nos_args))
        return resultado.sucesso(unidade)
        
    # Criação de potência
    def potencia(self):
        return self.op_bin(self.chamada, (lexico.T_POW, ), self.fator)

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

    # Definindo uma função
    def func_def(self):
        resultado = ResultadoParser()

        if not self.token_atual.token_bate(lexico.T_KEYWORD, 'FUN'):
            return resultado.falha(erros.ErroSintaxeInvalida("Era esperado 'FUN'",self.token_atual.pos_com))
        
        resultado.registro_avanc()
        self.avanc()
        if self.token_atual.tipo == lexico.T_IDENTIFICADOR:
            token_nome_fun = self.token_atual
            resultado.registro_avanc()
            self.avanc()
            if self.token_atual.tipo != lexico.T_LPAREN:
                return resultado.falha(erros.ErroSintaxeInvalida("Era esperado um ' ' ", self.token_atual.pos))
        else:
            token_nome_fun = None
            if self.token_atual.tipo != lexico.T_LPAREN:
                return resultado.falha(erros.ErroSintaxeInvalida("Era esperado um identificador de variável ou '(' ", self.token_atual.pos))
        resultado.registro_avanc()
        self.avanc()
        
        # Lembrando que podemos ter funções com e sem parâmetros
        tokens_args = []
        if self.token_atual.tipo == lexico.T_IDENTIFICADOR:
            tokens_args.append(self.token_atual)
            resultado.registro_avanc()
            self.avanc()
            while self.token_atual.tipo == lexico.T_VIRG:
                resultado.registro_avanc()
                self.avanc()
                if self.token_atual.tipo != lexico.T_IDENTIFICADOR:
                    return resultado.falha(erros.ErroSintaxeInvalida("Era esperado um identificador de variável", self.token_atual.pos))
                tokens_args.append(self.token_atual)
                resultado.registro_avanc()
                self.avanc()
            if self.token_atual.tipo != lexico.T_RPAREN:
                return resultado.falha(erros.ErroSintaxeInvalida("Era esperado um ')' ", self.token_atual.pos))
        
        else:
            if self.token_atual.tipo != lexico.T_RPAREN:
                return resultado.falha(erros.ErroSintaxeInvalida("Era esperado um ')' ", self.token_atual.pos))
        resultado.registro_avanc()
        self.avanc()

        if self.token_atual.tipo != lexico.T_SETA:
            return resultado.falha(erros.ErroSintaxeInvalida("Era esperado uma '->' ", self.token_atual.pos))
        
        resultado.registro_avanc()
        self.avanc()
        no_corpo = resultado.registro(self.expressao())
        if resultado.erro: 
            return resultado
        
        return resultado.sucesso(NoDefFun(token_nome_fun ,tokens_args, no_corpo))

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