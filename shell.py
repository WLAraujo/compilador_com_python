#####################################################
# Esse arquivo codifica o shell da nossa linguagem  #
#####################################################

import interfaces

while True:
    comando = input('basic >> ')
    if comando == 'sair()':
        break
    resultado, erro = interfaces.run(comando, "<<Entrada do shell>>")
    if erro:
        print(erro.str_retorno())
    elif resultado:
        print(resultado.__rep__())
    