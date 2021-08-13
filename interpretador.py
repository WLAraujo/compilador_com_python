#########################################################################################################################################
# Nesse arquivo desenvolveremos o interpretador da nossa linguagem. O que o interpretador faz é pegar a árvore resultado do processo de #
# parsing e decidir qual o código que deve ser executado, em especial qual a ordem das operações que devem ser realizadas.              #
#########################################################################################################################################

import erros
import lexico

#############################
## Classe do Interpretador ##
#############################

class Interpretador:

    # Método de visita que pega um nó e vai visitando recursivamente seus filhos, queremos que esse método comporte-se de maneira
    # diferente para cada tipo de nó
    def visita(self, no, contexto):
        tipo_visita = f'visita_{type(no).__name__}'
        metodo = getattr(self, tipo_visita, self.sem_visita)
        return metodo(no, contexto)

    def sem_visita(self, no, contexto):
        raise Exception(f'Sem método de visita visita_{type(no).__name__}')

    def visita_NoNumero(self, no, contexto):
        return ResultadoRT().sucesso(Numero(no.token.valor).def_contexto(contexto).def_pos(no.pos_com))

    def visita_NoAcessoVar(self, no, contexto):
        resultado = ResultadoRT()
        nome_var = no.token_var.valor
        valor_var = contexto.tabela_simbolos.get(nome_var)
        if valor_var == None:
            return resultado.falha(erros.ErroRunTime(f'{nome_var} não  foi definido como variável', no.pos_com, contexto))
        return resultado.sucesso(valor_var)

    def visita_NoAtribuiVar(self, no, contexto):
        resultado = ResultadoRT()
        nome_var = no.token_var.valor
        valor_var = resultado.registro(self.visita(no.valor_no, contexto))
        if resultado.erro:
            return resultado
        contexto.tabela_simbolos.set(nome_var, valor_var)
        return resultado.sucesso(valor_var)

    def visita_NoOpBinaria(self, no, contexto):
        capsula_resultado = ResultadoRT()
        esq = capsula_resultado.registro(self.visita(no.no_esq, contexto))
        if capsula_resultado.erro:
            return capsula_resultado.erro
        dir = capsula_resultado.registro(self.visita(no.no_dir, contexto))
        if capsula_resultado.erro:
            return capsula_resultado.erro
        
        if no.token.tipo == lexico.T_PLUS:
            resultado, erro = esq.adicionar_a(dir)
        elif no.token.tipo == lexico.T_MINUS:
            resultado, erro = esq.subtrair_de(dir)
        elif no.token.tipo == lexico.T_MULT:
            resultado, erro = esq.multiplicar_por(dir)
        elif no.token.tipo == lexico.T_DIV:
            resultado, erro = esq.dividir_por(dir)
        elif no.token.tipo == lexico.T_POW:
            resultado, erro = esq.elevar_a(dir)
        elif no.token.tipo == lexico.T_EHIGUAL:
            resultado, erro = esq.compara_eh_igual(dir)
        elif no.token.tipo == lexico.T_NIGUAL:
            resultado, erro = esq.compara_n_eh_igual(dir)
        elif no.token.tipo == lexico.T_MENORQ:
            resultado, erro = esq.compara_menor(dir)
        elif no.token.tipo == lexico.T_MAIORQ:
            resultado, erro = esq.compara_maior(dir)
        elif no.token.tipo == lexico.T_MENORIGUALQ:
            resultado, erro = esq.compara_menor_igual(dir)
        elif no.token.tipo == lexico.T_MAIORIGUALQ:
            resultado, erro = esq.compara_maior_igual(dir)
        elif no.token.token_bate(lexico.T_KEYWORD, 'E'):
            resultado, erro = esq.e_logico(dir)
        elif no.token.token_bate(lexico.T_KEYWORD, 'OU'):
        	resultado, erro = esq.ou_logico(dir)

        if erro:
            return capsula_resultado.falha(erro)
        else:
            return capsula_resultado.sucesso(resultado.def_pos(no.pos_com))
    
    def visita_NoOpUnaria(self, no, contexto):
        resultado = ResultadoRT()

        numero = resultado.registro(self.visita(no.no, contexto))
        if resultado.erro:
            return resultado
    
        erro = None
        if no.token_op.tipo == lexico.T_MINUS:
            numero, erro = numero.multiplicar_por(Numero(-1))
        elif no.token_op.token_bate(lexico.T_KEYWORD, 'NAO'):
            numero, erro = numero.negar()

        if erro:
            return resultado.falha(erro)
        else:
            return resultado.sucesso(numero.def_pos(no.pos_com))

##############################
## Armazenamento de Valores ##
##############################

class Numero:

    # Método construtor
    def __init__(self, valor):
        self.valor = valor
        self.def_pos()
        self.def_contexto()

    # Método que mantém registro de onde está o número no código
    def def_pos(self, pos_com=None):
        self.pos_com = pos_com
        return self

    def def_contexto(self, contexto = None):
        self.contexto = contexto
        return self

    # Métodos responsáveis pelas operações aritméticas, lógicas e de comparação
    def adicionar_a(self, outro):
        if isinstance(outro, Numero):
            return Numero(self.valor + outro.valor).def_contexto(self.contexto), None
    def subtrair_de(self, outro):
        if isinstance(outro, Numero):
            return Numero(self.valor - outro.valor).def_contexto(self.contexto), None
    def multiplicar_por(self, outro):
        if isinstance(outro, Numero):
            return Numero(self.valor * outro.valor).def_contexto(self.contexto), None
    def dividir_por(self, outro):
        if isinstance(outro, Numero):
            if outro.valor == 0:
                return None, erros.ErroRunTime("Divisão por 0", outro.pos_com, self.contexto)
            return Numero(self.valor / outro.valor).def_contexto(self.contexto), None
    def elevar_a(self, outro):
        if isinstance(outro, Numero):
            return Numero(self.valor ** outro.valor).def_contexto(self.contexto), None
    def compara_eh_igual(self, outro):
        if isinstance(outro, Numero):
            return Numero(int(self.valor == outro.valor)).def_contexto(self.contexto), None
    def compara_n_eh_igual(self, outro):
        if isinstance(outro, Numero):
            return Numero(int(self.valor != outro.valor)).def_contexto(self.contexto), None
    def compara_menor(self, outro):
        if isinstance(outro, Numero):
            return Numero(int(self.valor < outro.valor)).def_contexto(self.contexto), None
    def compara_maior(self, outro):
        if isinstance(outro, Numero):
            return Numero(int(self.valor > outro.valor)).def_contexto(self.contexto), None
    def compara_menor_igual(self, outro):
        if isinstance(outro, Numero):
            return Numero(int(self.valor <= outro.valor)).def_contexto(self.contexto), None
    def compara_maior_igual(self, outro):
        if isinstance(outro, Numero):
            return Numero(int(self.valor >= outro.valor)).def_contexto(self.contexto), None
    def e_logico(self, outro):
        if isinstance(outro, Numero):
            return Numero(int(self.valor and outro.valor)).def_contexto(self.contexto), None
    def ou_logico(self, outro):
        if isinstance(outro, Numero):
            return Numero(int(self.valor or outro.valor)).def_contexto(self.contexto), None
    def negar(self):
        return Numero(1 if self.value == 0 else 0).def_contexto(self.contexto), None

    # Método que devolve o número
    def __rep__(self):
        return str(self.valor)

####################################
## Classe de Resultados de RunTime ##
####################################

# Classe com função de manter vigilância sobre o comportamento do interpretador, parando a execução em caso de erro
class ResultadoRT:

    # Método construtor
    def __init__(self):
        self.valor = None
        self.erro = None
    
    # Método de registro na classe ResultadoRT
    def registro(self, resultado):
        if resultado.erro:
            self.erro = resultado.erro
        return resultado.valor

    # Método que representa o sucesso da operação com valor do processo
    def sucesso(self, valor):
        self.valor = valor
        return self
    
    # Método que representa a falha da operação 
    def falha(self, erro):
        self.erro = erro
        return self

##################################
## Classe de Tabela de Símbolos ##
##################################

# A ideia dessa classe é manter vigilância sobre todas as variáveis, seus nomes e valores
# Como cada função possui um escopo e vai precisar de uma tabela de símbolos, toda tabela de símbolos possui uma tabela mãe
class TabelaSimbolos:

    # Método construtor
    def __init__(self):
        self.simbolos = {}
        self.pai = None

    # Dado o nome de uma variável vamos pegar seu valor
    def get(self, nome_var):
        valor = self.simbolos.get(nome_var, None)
        if valor == None and self.pai:
            return self.pai.get(nome_var)
        return valor
    
    # Dado o nome de uma variável e um valor vamos atribuir esse novo valor à variável
    def set(self, nome_var, valor):
        self.simbolos[nome_var] = valor

    # Dado o nome da variável vamos remover ela
    def remover(self, nome_var):
        del self.simbolos[nome_var]

# Vamos criar uma tabela de símbolos global para realmente englobar todos os contextos

tabela_simbolos_global = TabelaSimbolos()
tabela_simbolos_global.set('null', Numero(0))

########################
## Classe de Contexto ##
########################

# Classe que mantém o contexto atual do programa, isso é, a função sendo executada no momento
class Contexto:

    # Método construtor
    def __init__(self, nome_exibido, pai = None, pos_pai = None):
        self.nome_exibido = nome_exibido
        self.pai = pai
        self.pos_pai = pos_pai
        self.tabela_simbolos = None

#########################
## Função de Interface ##
#########################   

# Função de interface do interpretador
def interface(arv_parser):
    interpretador = Interpretador()
    contexto = Contexto('<local>')
    contexto.tabela_simbolos = tabela_simbolos_global
    resultado = interpretador.visita(arv_parser, contexto)
    return resultado.valor, resultado.erro


