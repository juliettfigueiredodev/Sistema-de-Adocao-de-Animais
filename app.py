import time
import os
from src import *

def limpar_tela():
    # Verifica o nome do sistema operacional
    if os.name == 'nt': # Windows
        os.system('cls')
    else: # Linux, macOS 
        os.system('clear')

MENU = '''
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

def main():

    while True:
        opcao = input (MENU)

        if opcao == '1':
            limpar_tela()
            #cadastrar_pet
        
        elif opcao == '2':
            limpar_tela()
            # cadastrar_adotante
        
        elif opcao == '3':
            limpar_tela()
            #realizar_reserva
        
        elif opcao == '4':
            limpar_tela()
            #adoção_efetiva
        
        elif opcao == '5':
            limpar_tela()
            #devolução
            

        elif opcao == '6':
            limpar_tela()
            #relatorio_top5
        
        elif opcao == '7':
            limpar_tela()
            #relatorio_taxa_adoção_porte_especie

        elif opcao == '8':
            limpar_tela()
            #relatorio_tempo_medio_entrada_adoção

        elif opcao == '9':  
            limpar_tela()
            #relatorio_adoções_canceladas_devoluções_motivo 

        elif opcao == 'S':
            print('🚶🏻🚶🏻🚶🏻🚶🏻🚶🏻')
            break

        else:
            print('''
        ⛔ Opção inválida, por favor selecione novamente a opção desejada.''')
            time.sleep(1)
            limpar_tela()

if __name__ == '__main__':
    main()
