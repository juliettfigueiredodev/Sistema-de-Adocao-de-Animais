import time
import os
from src import *
from datetime import datetime
from src.models.fila_espera import FilaEspera
from src.services.gestao_animal_service import GestaoAnimalService
from src.models.animal_status import AnimalStatus

from src.models.adotante import Adotante 
from src.models.cachorro import Cachorro

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
    [5] Devolução (Gera Quarentena/Devolvido) 😿

        📋📋 Relatórios 📋📋

    [6] TOP 5 🔥
    [7] Taxa de adoção espécie/porte
    [8] Tempo médio entre entrada e adoção
    [9] Adoções canceladas/devoluções por motivo
    [10] Reavaliar Animal (Sair da Quarentena) 🩺
    [11] Simular Expiração de Reserva (Acionar Fila) ⏳
    [12] Ver Fila de Espera Atual 👀
    [S] Sair do sistema 🚶🏻

    O que você quer fazer? => '''


def inicializar_dados_mock(fila_espera):
    """
    Cria dados iniciais para você não precisar cadastrar tudo do zero
    toda vez que rodar o app para testar.
    """
    animais = []

    # Animal ADOTADO (Para testar Devolução)
    rex = Cachorro(
        nome="Rex", porte="M", raca="SRD", sexo="M", 
        idade_meses=24, necessidade_passeio=5
    )
    # Simulando que já foi adotado
    rex._status = AnimalStatus.ADOTADO 
    animais.append(rex)

    # Animal RESERVADO (Para testar Fila/Expiração)
    toto = Cachorro(
        nome="Totó", porte="P", raca="Poodle", sexo="M", 
        idade_meses=12, necessidade_passeio=3
    )
    toto._status = AnimalStatus.RESERVADO
    animais.append(toto)

    # Adotantes na Fila (Para o Totó)
    # Adotante 1 (Score 80)
    adotante1 = Adotante(
        nome="João", idade=30, moradia="casa", area_util=100, 
        experiencia=True, criancas=False, outros_animais=False
    )
    fila_espera.adicionar(adotante1, pontuacao=80)

    # Adotante 2 (Score 95 - Prioritário)
    adotante2 = Adotante(
        nome="Maria", idade=25, moradia="apartamento", area_util=80, 
        experiencia=True, criancas=False, outros_animais=False
    )
    fila_espera.adicionar(adotante2, pontuacao=95)

    return animais


def main():
    # --- INICIALIZAÇÃO DOS SERVIÇOS ---
    fila_espera = FilaEspera()
    gestao_service = GestaoAnimalService()
    
    # Carrega dados para testes
    banco_animais = inicializar_dados_mock(fila_espera)

    while True:
        # Exibe status rápido para debug
        print("\n--- 🔍 STATUS DOS ANIMAIS NA MEMÓRIA ---")
        for i, animal in enumerate(banco_animais):
            print(f"[{i}] {animal.nome} ({animal.status.value})")
        print("----------------------------------------")

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
        
        # DEVOLUÇÃO
        elif opcao == '5':
            limpar_tela()
            print("=== 😿 DEVOLUÇÃO DE ANIMAL ===")
            try:
                idx = int(input("Digite o índice do animal (ex: 0 para Rex): "))
                animal = banco_animais[idx]
                
                print(f"Processando devolução de: {animal.nome}")
                motivo = input("Qual o motivo da devolução? ")
                tem_problema = input("O animal apresentou problema de saúde/comportamento? (S/N): ").upper() == 'S'

                gestao_service.processar_devolucao(animal, motivo, tem_problema)
                input("\nDevolução registrada! Pressione Enter...")
            
            except (ValueError, IndexError):
                print("❌ Animal inválido.")
                time.sleep(1)
            except Exception as e:
                print(f"❌ Erro: {e}")
                input()
            

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
        
        # REAVALIAÇÃO
        elif opcao == '10':
            limpar_tela()
            print("=== 🩺 REAVALIAÇÃO DE QUARENTENA ===")
            try:
                idx = int(input("Digite o índice do animal em Quarentena: "))
                animal = banco_animais[idx]
                
                if animal.status not in [AnimalStatus.QUARENTENA, AnimalStatus.DEVOLVIDO]:
                    print(f"⚠️ Este animal está {animal.status.value}, não pode ser reavaliado.")
                else:
                    apto = input(f"O animal {animal.nome} está apto para adoção? (S/N): ").upper() == 'S'
                    gestao_service.reavaliar_quarentena(animal, apto)
                    input("\nReavaliação concluída! Pressione Enter...")
            
            except (ValueError, IndexError):
                print("❌ Animal inválido.")
                time.sleep(1)
            except Exception as e:
                print(f"❌ Erro: {e}")
                input()

        # FILA DE ESPERA E EXPIRAÇÃO
        elif opcao == '11':
            limpar_tela()
            print("=== ⏳ SIMULA EXPIRAÇÃO DE RESERVA ===")
            try:
                idx = int(input("Digite o índice do animal reservado (ex: 1 para Totó): "))
                animal = banco_animais[idx]

                print(f"Simulando fim do prazo de reserva para {animal.nome}...")
                gestao_service.verificar_expiracao_reserva(animal, fila_espera)
                input("\nProcesso finalizado! Pressione Enter...")

            except (ValueError, IndexError):
                print("❌ Animal inválido.")
            except Exception as e:
                print(f"❌ Erro: {e}")
                input()

        elif opcao == '12':
            limpar_tela()
            print(f"=== 👀 FILA DE ESPERA ATUAL ===")
            print(fila_espera)
            input("\nPressione Enter...")

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
