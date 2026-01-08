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
    🐾🐾 Adote um Pet! 🐾🐾

    [1] Cadastrar pet 🐶
    [2] Cadastrar adotante👤


    [3] Reservar 🤩
    [4] Adoção efetiva 😁
    [5] Devolução 😿

    📋📋 Relatórios 📋📋
    [6] TOP 5 🔥
    [7] Taxa de adoção espécie/porte
    [8] Tempo médio entre entrada e adoção
    [9] Adoções canceladas/devoluções por motivo
    [S] Sair do sistema 🚶🏻

    O que você quer fazer? => '''

while True:
    opcao = input (menu)

    if opcao == '1':
        limpar_tela()
        # id_pet = len(pets) + 1
        #cadastrar_pet(pets)
    
    elif opcao == '2':
        limpar_tela()
        #  id_pessoa = len(pessoas) + 1
        # cadastrar_humano(pessoas) 
    
    elif opcao == '3':
        limpar_tela()
        # print(lista_pets)
        # cod_reserva = input('Digite o código da reserva: ')
        # reserva(cod_reserva)
    
    elif opcao == '4':
        limpar_tela()
        pass
    
    elif opcao == '5':
        limpar_tela()
        #implementar interface devolução
        pass

    elif opcao == '6':
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
