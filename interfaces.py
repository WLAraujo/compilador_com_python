#######################################################################################################################################
# Nesse arquivo serão feitas as interações com o analisadore léxico, o parser e o interpretador através dos seus métodos de interface #
#######################################################################################################################################

import lexico
import parser

def run(texto, nome_arq):

    # Criando os tokens
    tokens, erro = lexico.interface(texto, nome_arq)
    if erro:
        return None, erro

    # Criando a árvore de parsing
    arv_parser = parser.interface(tokens)
    return arv_parser, None