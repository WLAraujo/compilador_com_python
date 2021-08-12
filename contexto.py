###################################################################################################################################
# Nesse arquivo vamos desenvolver uma forma de mostrar para o usuário da linguagem onde estão ocorrendo os processos em execução. #
# Assim, quando um erro for lançado ele pode identificar qual o caminho do erro.                                                  #
###################################################################################################################################

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