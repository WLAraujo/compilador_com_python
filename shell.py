# Esse arquivo codifica o shell da nossa linguagem.

import lexico

while True:
    comando = input('basic >> ')
    resultado, erro = lexico.interface(comando)
    if erro:
        print(erro.str_retorno())
    else:
        print(resultado)