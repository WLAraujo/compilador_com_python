#########################################################################################################################################
# Nesse arquivo desenvolveremos o interpretador da nossa linguagem. O que o interpretador faz é pegar a árvore resultado do processo de #
# parsing e decidir qual o código que deve ser executado, em especial qual a ordem das operações que devem ser realizadas.              #
#########################################################################################################################################

from contexto import Contexto
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

    # Métodos responsáveis pelas operações aritméticas
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
    
    def falha(self, erro):
        self.erro = erro
        return self

#########################
## Função de Interface ##
#########################   

# Função de interface do interpretador
def interface(arv_parser):
    interpretador = Interpretador()
    contexto = Contexto('<local>')
    resultado = interpretador.visita(arv_parser, contexto)
    return resultado.valor, resultado.erro


