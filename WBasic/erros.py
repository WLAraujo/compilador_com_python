###############################################################################################################
# Nesse módulo definiremos os erros que podem acontecer durante a execução da nossa linguagem de programação  #
###############################################################################################################

#####################
## Definição Erros ##
#####################

# Classe de erro genérica, superior na hierárquia d
class Erro:

    # Inicializador da classe
    def __init__(self, nome_erro, detalhes, pos_inicio):
        self.nome_erro = nome_erro
        self.detalhes = detalhes
        self.pos_inicio = pos_inicio
    
    # Mensagem de retorno do erro
    def str_retorno(self):
        self.msg_erro = f'{self.nome_erro} : {self.detalhes}\nArquivo: {self.pos_inicio.nome_arq}\nLinha: {self.pos_inicio.lin + 1}'
        return self.msg_erro

# Classe de erro de caractere ilegal, erro identificável no analisador léxico
class ErroCharIlegal(Erro):

    # Inicializador do erro char ilegal
    def __init__(self, detalhes, pos_inicio):
        super().__init__("Caractere Ilegal", detalhes, pos_inicio)

# Classe de erro de sintaxe inválida, erro identificável no parser
class ErroSintaxeInvalida(Erro):

    # Inicializador do erro
    def __init__(self, detalhes, pos_inicio):
        super().__init__("Sintaxe Inválida", detalhes, pos_inicio)

# Classe de erro runtime, afinal o erro nesse caso aconteceria especificamente no tempo de execução da interpretação da nossa linguagem
class ErroRunTime(Erro):

    # Inicializador do erro
    def __init__(self, detalhes, pos_inicio, contexto):
        super().__init__("Erro de RunTime", detalhes, pos_inicio)
        self.contexto = contexto
    
    def str_retorno(self):
        self.msg_erro = self.rastrear_erro()
        self.msg_erro += f'{self.nome_erro} : {self.detalhes}\nArquivo: {self.pos_inicio.nome_arq}\nLinha: {self.pos_inicio.lin + 1}'
        return self.msg_erro

    def rastrear_erro(self):
        resultado = ''
        pos = self.pos_inicio
        contexto = self.contexto
        while contexto:
            resultado = f'Arquivo {pos.nome_arq}, linha {str(pos.lin + 1)}, em {contexto.nome_exibido}\n' + resultado
            pos = contexto.pos_pai
            contexto = contexto.pai
        return resultado

# Classe de erro que é lançada quando temos a expectativa por um caractere mas recebemos outro
class ErroCharEsperado(Erro):
    def __init__(self, detalhes, pos_com):
        super().__init__('Outro caractere esperado', pos_com)