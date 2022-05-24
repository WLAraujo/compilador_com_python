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
        raise Exception(f'Sem método de visita visita_{type(no)}')

    def visita_NoNumero(self, no, contexto):
        return ResultadoRT().sucesso(Numero(no.token.valor).set_contexto(contexto).set_pos(no.pos_com))

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
            return capsula_resultado.sucesso(resultado.set_pos(no.pos_com))
    
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
            return resultado.sucesso(numero.set_pos(no.pos_com))
    
    def visita_NoSe(self, no, contexto):
        resultado = ResultadoRT()
        for condicao, expressao in no.casos:
            valor_condicao = resultado.registro(self.visita(condicao, contexto))
            if resultado.erro:
                return resultado
            if valor_condicao.eh_vdd():
                expressao_valor = resultado.registro(self.visita(expressao, contexto))
                if resultado.erro:
                    return resultado
                return resultado.sucesso(expressao_valor)
        if no.caso_senao:
            valor_senao = resultado.registro(self.visita(no.caso_senao, contexto))
            if resultado.erro:
                return resultado
            return resultado.sucesso(valor_senao)
        return resultado.sucesso(None)

    def visita_NoPara(self, no, contexto):
        resultado = ResultadoRT()
        valor_inicial = resultado.registro(self.visita(no.valor_inicial, contexto))
        if resultado.erro:
            return resultado
        valor_final = resultado.registro(self.visita(no.valor_final, contexto))
        if resultado.erro:
                return resultado
        if no.valor_passo:
            valor_passo = resultado.registro(self.visita(no.valor_passo, contexto))
            if resultado.erro:
                return erros
        else:
            valor_passo = Numero(1)
        i = valor_inicial.valor
        if valor_passo.valor >= 0:
            condicao = True if i < valor_final.valor else False
        else:
            condicao = True if i > valor_final.valor else False
        while condicao:
            contexto.tabela_simbolos.set(no.token_var.valor, Numero(i))
            i+=valor_passo.valor
            resultado.registro(self.visita(no.no_corpo, contexto))
            if resultado.erro:
                return resultado
            if valor_passo.valor >= 0:
                condicao = True if i < valor_final.valor else False
            else:
                condicao = True if i > valor_final.valor else False
        return resultado.sucesso(None)

    def visita_NoEnquanto(self, no, contexto):
        resultado = ResultadoRT()
        while True:
            condicao = resultado.registro(self.visita(no.no_condicao, contexto)) 
            if resultado.erro:
                return resultado
            if not condicao.eh_vdd():
                break
            resultado.registro(self.visita(no.no_corpo, contexto))
            if resultado.erro:
                return resultado
        return resultado.sucesso(None)      

    def visita_NoDefFun(self, no, contexto):
        resultado = ResultadoRT()
        nome = no.token_nome_fun.valor if no.token_nome_fun else None
        no_corpo = no.no_corpo
        args = [nome_arg.valor for nome_arg in no.tokens_fun_args]
        valor = Funcao(nome, no_corpo, args).set_contexto(contexto).set_pos(no.pos_com)
		
        # Caso a função não seja anônima temos que setar um novo contexto para ela
        if no.token_nome_fun:
            contexto.tabela_simbolos.set(nome, valor)
            
        return resultado.sucesso(valor)
    
    def visita_NoChamadaFun(self, no, contexto):
        resultado = ResultadoRT()
        args = []

        # Checamos se existe erro na função em si
        no_a_chamar = resultado.registro(self.visita(no.no_a_chamar, contexto))
        if resultado.erro: 
            return resultado
        no_a_chamar = no_a_chamar.copia().set_pos(no.pos_com)

        # Checamos erros nos nossos argumentos
        for no_arg in no.nos_args:
            args.append(resultado.registro(self.visita(no_arg, contexto)))
            if resultado.erro: 
                return resultado

        retorna_valor = resultado.registro(no_a_chamar.executar(args))
        if resultado.erro: 
            return resultado
        return resultado.sucesso(retorna_valor)

    def visita_NoString(self, no, contexto):
        return ResultadoRT().sucesso(String(no.token.valor).set_contexto(contexto).set_pos(no.pos_com))

##############################
## Armazenamento de Valores ##
##############################

# Classe mãe para classes que armazenam valores
class Valor():

    def __init__(self):
        self.set_pos()
        self.set_contexto()
    
    def set_pos(self, pos_com = None):
        self.pos_com = pos_com
        return self

    def set_contexto(self, contexto = None):
        self.contexto = contexto
        return self
    
    # Os métodos abaixo só funcionam caso não ocorra sobrescrita de métodos

    # Operações de números
    def adicionar_a(self, outro):
        return None, self.op_ilegal(outro)
    def subtrair_de(self, outro):
        return None, self.op_ilegal(outro)
    def multiplicar_por(self, outro):
        return None, self.op_ilegal(outro)
    def dividir_por(self, outro):
        return None, self.op_ilegal(outro)
    def elevar_a(self, outro):
        return None, self.op_ilegal(outro)
    def compara_eh_igual(self, outro):
        return None, self.op_ilegal(outro)
    def compara_n_eh_igual(self, outro):
        return None, self.op_ilegal(outro)
    def compara_menor(self, outro):
        return None, self.op_ilegal(outro)
    def compara_maior(self, outro):
        return None, self.op_ilegal(outro)
    def compara_menor_igual(self, outro):
        return None, self.op_ilegal(outro)
    def compara_maior_igual(self, outro):
        return None, self.op_ilegal(outro)
    def e_logico(self, outro):
        return None, self.op_ilegal(outro)
    def ou_logico(self, outro):
        return None, self.op_ilegal(outro)
    def negar(self):
        return None, self.op_ilegal()

    # Operações de funções
    def executar(self, args):
        return ResultadoRT().falha(self.op_ilegal)

    # Operações genéricas
    def copia(self):
        raise Exception('Nenhum método de cópia foi definido')
    def eh_vdd(self):
        return False
    
    # Método que lança o erro RT de operação ilegal para um tipo de valor
    def op_ilegal(self, outro = None):
        if not outro:
            outro = self
        return erros.ErroRunTime('Operação Ilegal para o tipo de valor', self.pos_com, self.contexto)

# Classe que representa os números
class Numero(Valor):

    # Método construtor
    def __init__(self, valor):
        super().__init__()
        self.valor = valor
        self.set_pos()
        self.set_contexto()

    # Método que mantém registro de onde está o número no código
    def set_pos(self, pos_com=None):
        self.pos_com = pos_com
        return self

    def set_contexto(self, contexto = None):
        self.contexto = contexto
        return self

    # Métodos responsáveis pelas operações aritméticas, lógicas e de comparação
    def adicionar_a(self, outro):
        if isinstance(outro, Numero):
            return Numero(self.valor + outro.valor).set_contexto(self.contexto), None
        else:
            return None, Valor.op_ilegal(self, outro)
    def subtrair_de(self, outro):
        if isinstance(outro, Numero):
            return Numero(self.valor - outro.valor).set_contexto(self.contexto), None
        else:
            return None, Valor.op_ilegal(self, outro)
    def multiplicar_por(self, outro):
        if isinstance(outro, Numero):
            return Numero(self.valor * outro.valor).set_contexto(self.contexto), None
        else:
            return None, Valor.op_ilegal(self, outro)
    def dividir_por(self, outro):
        if isinstance(outro, Numero):
            if outro.valor == 0:
                return None, erros.ErroRunTime("Divisão por 0", outro.pos_com, self.contexto)
            return Numero(self.valor / outro.valor).set_contexto(self.contexto), None
        else:
            return None, Valor.op_ilegal(self, outro)
    def elevar_a(self, outro):
        if isinstance(outro, Numero):
            return Numero(self.valor ** outro.valor).set_contexto(self.contexto), None
        else:
            return None, Valor.op_ilegal(self, outro)
    def compara_eh_igual(self, outro):
        if isinstance(outro, Numero):
            return Numero(int(self.valor == outro.valor)).set_contexto(self.contexto), None
        else:
            return None, Valor.op_ilegal(self, outro)
    def compara_n_eh_igual(self, outro):
        if isinstance(outro, Numero):
            return Numero(int(self.valor != outro.valor)).set_contexto(self.contexto), None
        else:
            return None, Valor.op_ilegal(self, outro)
    def compara_menor(self, outro):
        if isinstance(outro, Numero):
            return Numero(int(self.valor < outro.valor)).set_contexto(self.contexto), None
        else:
            return None, Valor.op_ilegal(self, outro)
    def compara_maior(self, outro):
        if isinstance(outro, Numero):
            return Numero(int(self.valor > outro.valor)).set_contexto(self.contexto), None
        else:
            return None, Valor.op_ilegal(self, outro)
    def compara_menor_igual(self, outro):
        if isinstance(outro, Numero):
            return Numero(int(self.valor <= outro.valor)).set_contexto(self.contexto), None
        else:
            return None, Valor.op_ilegal(self, outro)
    def compara_maior_igual(self, outro):
        if isinstance(outro, Numero):
            return Numero(int(self.valor >= outro.valor)).set_contexto(self.contexto), None
        else:
            return None, Valor.op_ilegal(self, outro)
    def e_logico(self, outro):
        if isinstance(outro, Numero):
            return Numero(int(self.valor and outro.valor)).set_contexto(self.contexto), None
        else:
            return None, Valor.op_ilegal(self, outro)
    def ou_logico(self, outro):
        if isinstance(outro, Numero):
            return Numero(int(self.valor or outro.valor)).set_contexto(self.contexto), None
        else:
            return None, Valor.op_ilegal(self, outro)
    def negar(self):
        return Numero(1 if self.valor == 0 else 0).set_contexto(self.contexto), None
    def copia(self):
        copia = Numero(self.valor)
        copia.set_pos(self.pos_com)
        copia.set_contexto(self.contexto)
        return copia
    def eh_vdd(self):
        return self.valor != 0
    def __rep__(self):
        return str(self.valor)

    # Método que devolve se o valor representa verdadeiro ou falso
    def eh_vdd(self):
        return self.valor != 0

    # Método que devolve o número
    def __rep__(self):
        return str(self.valor)

# Classe que representa as funções
class Funcao(Valor):

    def __init__(self, nome, no_corpo, args):
        super().__init__()
        self.nome = nome or "anonima"
        self.no_corpo = no_corpo
        self.args = args

    def executar(self, args):
        resultado = ResultadoRT()
        interpretador = Interpretador()
        # Lembrando que sempre que criamos uma nova função criamos também um novo contexto
        novo_contexto = Contexto(self.nome, self.contexto, self.pos_com)
        novo_contexto.tabela_simbolos = TabelaSimbolos(novo_contexto.pai.tabela_simbolos)

        # Verificando problema de muitos argumentos passados
        if len(args) > len(self.args):
            return resultado.falha(erros.ErroRunTime(f"Muitos argumentos foram passados em {self.nome}",self.pos_com, self.contexto))
    
        # Verificando problema de poucos argumentos passados
        if len(args) < len(self.args):
        	return resultado.falha(erros.ErroRunTime(f"Poucos argumentos foram passados em {self.nome}",self.pos_com, self.contexto))

        # Para o novo contexto criado vamos adicionar cada variável
        for i in range(len(args)):
            nome_arg = self.args[i]
            valor_arg = args[i]
            valor_arg.set_contexto(novo_contexto)
            novo_contexto.tabela_simbolos.set(nome_arg, valor_arg)

        # Chamamos o interpretador para fazer uma visita dentro do contexto criado
        valor = resultado.registro(interpretador.visita(self.no_corpo, novo_contexto))
        if resultado.erro: 
            return resultado
        return resultado.sucesso(valor)

    def copia(self):
        copia = Funcao(self.nome, self.no_corpo, self.args)
        copia.set_contexto(self.contexto)
        copia.set_pos(self.set_pos)
        return copia

    def __rep__(self):
        return f'<função> : {self.nome}'

# Classe que representa Strings
class String(Valor):
    
    def __init__(self, valor):
        super().__init__()
        self.valor = valor

    def adicionar_a(self, outra):
        if isinstance(outra, String):
            return String(self.valor + outra.valor).set_contexto(self.contexto), None
        else:
            return None, Valor.op_ilegal(self, outra)

    def multiplicar_por(self, vezes):
        if isinstance(vezes, Numero):
            return String(self.valor * vezes.valor).set_contexto(self.contexto), None
        else:
            return None, Valor.op_ilegal(self, vezes)

    def eh_vdd(self):
        return len(self.valor)>0

    def copia(self):
        copia = String(self.valor)
        copia.set_contexto(self.contexto)
        copia.set_pos(self.set_pos)
        return copia

    def __rep__(self):
        return f'{self.valor}'

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
        self.valor = None
        return self

##################################
## Classe de Tabela de Símbolos ##
##################################

# A ideia dessa classe é manter vigilância sobre todas as variáveis, seus nomes e valores
# Como cada função possui um escopo e vai precisar de uma tabela de símbolos, toda tabela de símbolos possui uma tabela mãe
class TabelaSimbolos:

    # Método construtor
    def __init__(self, pai = None):
        self.simbolos = {}
        self.pai = pai

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
    if type(resultado) == erros.ErroRunTime:
        return None, resultado
    return resultado.valor, resultado.erro


