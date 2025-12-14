import time
import os
from .src import *

def limpar_tela():
    # Verifica o nome do sistema operacional
    if os.name == 'nt': # Windows
        os.system('cls')
    else: # Linux, macOS 
        os.system('clear')

menu = '''
    🐾🐾 Adote seu Humano! 🐾🐾

    [p] Cadastrar pet 🐶
    [h] Cadastrar humano👤


    [r] Reservar 🤩
    [a] Adoção efetiva 😁
    [d] Devolução 😿
    [t] TOP 5 🔥
    [S] Sair do sistema 🚶🏻

    O que você quer fazer? => '''

while True:
    opcao = input (menu)

    if opcao == 'p':
        limpar_tela()
        # id_pet = len(pets) + 1
        #cadastrar_pet(pets)
    
    elif opcao == 'h':
        limpar_tela()
        #  id_pessoa = len(pessoas) + 1
        # cadastrar_humano(pessoas) 
    
    elif opcao == 'r':
        limpar_tela()
        # print(lista_pets)
        # cod_reserva = input('Digite o código da reserva: ')
        # reserva(cod_reserva)
    
    elif opcao == 'a':
        limpar_tela()
        pass
    
    elif opcao == 'd':
        limpar_tela()
        #implementar interface devolução
        pass

    elif opcao == 't':
        limpar_tela()
        #print(listar_top5())
    
    elif opcao == 'S':
        print('🚶🏻🚶🏻🚶🏻🚶🏻🚶🏻')
        break

    else:
        print('''
    ⛔ Opção inválida, por favor selecione novamente a opção desejada.''')
        time.sleep(1)
        limpar_tela()

