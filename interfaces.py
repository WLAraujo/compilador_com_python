#######################################################################################################################################
# Nesse arquivo serão feitas as interações com o analisadore léxico, o parser e o interpretador através dos seus métodos de interface #
#######################################################################################################################################

import interpretador
import lexico
import parser

def run(texto, nome_arq):

    # Criando os tokens
    tokens, erro = lexico.interface(texto, nome_arq)
    if erro:
        return None, erro

    # Criando a árvore de parsing
    arv_parser, erro = parser.interface(tokens)
    if erro:
        return None, erro
    
    # Criando o interpretador
    resultado, erro = interpretador.interface(arv_parser)
    return resultado, erro