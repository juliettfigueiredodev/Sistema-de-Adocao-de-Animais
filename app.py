"""
Sistema de Adoção de Animais - Interface CLI
Aplicação principal com menu interativo e sistema de logs.
"""

import sys
from pathlib import Path
from typing import List, Optional

from src.infrastructure.animal_repository import (
    AnimalRepository,
    AnimalNaoEncontradoError,
)
from src.infrastructure.adotante_repository import AdotanteRepository
from src.infrastructure.fila_repository import FilaRepository
from src.infrastructure.settings_loader import SettingsLoader
from src.infrastructure.event_logger import logger
from src.models.adotante import Adotante
from src.models.animal import Animal
from src.models.animal_status import AnimalStatus
from src.models.cachorro import Cachorro
from src.models.gato import Gato
from src.models.fila_espera import FilaEspera
from src.services.adocao_service import AdocaoService
from src.services.compatibilidade_service import CompatibilidadeService
from src.services.expiracao_reserva import ExpiracaoReservaJob
from src.services.gestao_animal_service import GestaoAnimalService
from src.services.relatorio_service import RelatorioService
from src.services.reserva_service import ReservaService
from src.services.taxa_adocao import (
    TaxaPadrao,
    TaxaSenior,
    TaxaFilhote,
    TaxaEspecial,
)
from src.services.triagem_service import TriagemService
from src.validators.exceptions import (
    PoliticaNaoAtendidaError,
    ReservaInvalidaError,
    TransicaoDeEstadoInvalidaError,
    FilaVaziaError,
)


# ============================================================================
# CONSTANTES
# ============================================================================

MENU = """
╔════════════════════════════════════════════════════════════╗
║              🐾🐾 ADOTE UM PET! 🐾🐾                      ║
╚════════════════════════════════════════════════════════════╝

📝 CADASTROS
    [1] Cadastrar pet 🐶
    [2] Cadastrar adotante 👤

🏠 ADOÇÕES
    [3] Reservar animal 🤩
    [4] Efetivar adoção 😁
    [5] Processar devolução 😿

📊 RELATÓRIOS
    [6] TOP 5 animais mais adotáveis 🔥
    [7] Taxa de adoção por espécie/porte 📈
    [8] Tempo médio até adoção ⏱️
    [9] Devoluções por motivo 📉

🔧 GESTÃO
    [10] Reavaliar animal (sair da quarentena) 🩺
    [11] Simular expiração de reservas ⏳
    [12] Ver filas de espera 👀

    [S] Sair do sistema 🚪

╰─➤ Digite sua opção: """


# ============================================================================
# CLASSE PRINCIPAL DA APLICAÇÃO
# ============================================================================

class SistemaAdocao:
    """
    Classe principal que orquestra todo o sistema de adoção.
    
    Responsável por:
    - Inicializar repositórios e serviços
    - Gerenciar o menu interativo
    - Coordenar operações entre diferentes serviços
    - Registrar logs de eventos importantes
    """
    
    def __init__(self):
        """Inicializa o sistema carregando configurações e repositórios."""
        logger.log("SISTEMA_INICIADO", mensagem="Iniciando Sistema de Adoção de Animais")
        
        print("\n🐾 Inicializando Sistema de Adoção de Animais...\n")
        
        # Carrega configurações
        try:
            self.settings = SettingsLoader.carregar()
            print("✅ Configurações carregadas com sucesso")
            logger.log("CONFIGURACOES_CARREGADAS", sucesso=True)
        except Exception as e:
            print(f"❌ Erro ao carregar configurações: {e}")
            logger.log("ERRO_CONFIGURACOES", erro=str(e))
            sys.exit(1)
        
        # Inicializa repositórios
        self.animal_repo = AnimalRepository("data/animais.json")
        self.adotante_repo = AdotanteRepository("data/adotantes.json")
        self.fila_repo = FilaRepository("data/filas.json")
        
        try:
            self.animal_repo.load()
            print(f"✅ Repositório de animais carregado: {len(self.animal_repo)} animais")
        except Exception as e:
            print(f"⚠️  Aviso ao carregar animais: {e}")
            print("   Iniciando com repositório vazio...")
            logger.log("AVISO_CARREGAMENTO_ANIMAIS", erro=str(e))
        
        try:
            self.adotante_repo.load()
            print(f"✅ Repositório de adotantes carregado: {len(self.adotante_repo)} adotantes")
        except Exception as e:
            print(f"⚠️  Aviso ao carregar adotantes: {e}")
            print("   Iniciando com repositório vazio...")
            logger.log("AVISO_CARREGAMENTO_ADOTANTES", erro=str(e))
        
        try:
            self.fila_repo.load()
            print(f"✅ Filas de espera carregadas: {len(self.fila_repo)} filas")
        except Exception as e:
            print(f"⚠️  Aviso ao carregar filas: {e}")
            print("   Iniciando com filas vazias...")
            logger.log("AVISO_CARREGAMENTO_FILAS", erro=str(e))
        
        # Inicializa serviços
        self.triagem_service = TriagemService()
        
        duracao_reserva = self.settings["reserva"]["duracao_horas"]
        self.reserva_service = ReservaService(self.animal_repo, duracao_reserva)
        
        self.adocao_service = AdocaoService(self.animal_repo)
        self.gestao_service = GestaoAnimalService()
        self.relatorio_service = RelatorioService()
        self.expiracao_job = ExpiracaoReservaJob(self.animal_repo)
        
        print("✅ Todos os serviços inicializados\n")
        
        logger.log("SISTEMA_PRONTO",
                   animais=len(self.animal_repo),
                   adotantes=len(self.adotante_repo),
                   filas=len(self.fila_repo))
    
    # ========================================================================
    # MENU PRINCIPAL
    # ========================================================================
    
    def executar(self):
        """Loop principal do sistema - exibe menu e processa escolhas."""
        while True:
            try:
                opcao = input(MENU).strip().upper()
                
                logger.log("MENU_OPCAO_SELECIONADA", opcao=opcao)
                
                if opcao == "S":
                    self._sair()
                    break
                elif opcao == "1":
                    self._cadastrar_pet()
                elif opcao == "2":
                    self._cadastrar_adotante()
                elif opcao == "3":
                    self._reservar()
                elif opcao == "4":
                    self._adocao_efetiva()
                elif opcao == "5":
                    self._devolucao()
                elif opcao == "6":
                    self._top_5()
                elif opcao == "7":
                    self._taxa_adocao_especie_porte()
                elif opcao == "8":
                    self._tempo_medio_adocao()
                elif opcao == "9":
                    self._devolucoes_por_motivo()
                elif opcao == "10":
                    self._reavaliar_animal()
                elif opcao == "11":
                    self._simular_expiracao()
                elif opcao == "12":
                    self._ver_fila_espera()
                else:
                    print("\n❌ Opção inválida! Tente novamente.\n")
                    logger.log("MENU_OPCAO_INVALIDA", opcao=opcao)
                    
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrompido pelo usuário")
                logger.log("SISTEMA_INTERROMPIDO", motivo="KeyboardInterrupt")
                self._sair()
                break
            except Exception as e:
                print(f"\n❌ Erro inesperado: {e}\n")
                logger.log("ERRO_INESPERADO", erro=str(e), tipo=type(e).__name__)
    
    # ========================================================================
    # OPERAÇÕES DO MENU
    # ========================================================================
    
    def _cadastrar_pet(self):
        """Opção 1: Cadastrar novo animal no sistema."""
        print("\n" + "="*60)
        print("🐶 CADASTRO DE ANIMAL")
        print("="*60)
        
        try:
            # Escolhe espécie
            especie = input("Espécie (1-Cachorro / 2-Gato): ").strip()
            if especie not in ("1", "2"):
                print("❌ Espécie inválida!")
                return
            
            # Dados comuns
            nome = input("Nome: ").strip()
            if not nome:
                print("❌ Nome é obrigatório!")
                return
            
            raca = input("Raça: ").strip()
            if not raca:
                print("❌ Raça é obrigatória!")
                return
            
            sexo = input("Sexo (M/F): ").strip().upper()
            
            idade_meses = int(input("Idade (em meses): "))
            
            porte = input("Porte (P/M/G): ").strip().upper()
            if porte not in ("P", "M", "G"):
                print("❌ Porte inválido! Use P, M ou G")
                return
            
            # Temperamento (separado por vírgulas)
            temp_input = input("Temperamento (ex: docil,calmo,sociavel): ").strip()
            temperamento = [t.strip() for t in temp_input.split(",") if t.strip()]
            
            # Cria animal específico
            if especie == "1":
                necessidade_passeio = int(input("Necessidade de passeio (0-10): "))
                animal = Cachorro(
                    raca=raca,
                    nome=nome,
                    sexo=sexo,
                    idade_meses=idade_meses,
                    porte=porte,
                    necessidade_passeio=necessidade_passeio,
                    temperamento=temperamento,
                )
            else:
                independencia = int(input("Nível de independência (0-10): "))
                animal = Gato(
                    raca=raca,
                    nome=nome,
                    sexo=sexo,
                    idade_meses=idade_meses,
                    porte=porte,
                    independencia=independencia,
                    temperamento=temperamento,
                )
            
            # Adiciona ao repositório
            self.animal_repo.add(animal)
            self.animal_repo.save()
            
            logger.log("ANIMAL_CADASTRADO",
                       id=animal.id,
                       nome=animal.nome,
                       especie=animal.especie,
                       raca=animal.raca,
                       porte=animal.porte,
                       idade_meses=animal.idade_meses)
            
            print(f"\n✅ Animal cadastrado com sucesso!")
            print(f"   ID: {animal.id}")
            print(f"   {animal}")
            
        except ValueError as e:
            print(f"❌ Erro de validação: {e}")
            logger.log("ERRO_CADASTRO_ANIMAL", erro=str(e), tipo="ValidationError")
        except Exception as e:
            print(f"❌ Erro ao cadastrar: {e}")
            logger.log("ERRO_CADASTRO_ANIMAL", erro=str(e), tipo=type(e).__name__)
    
    def _cadastrar_adotante(self):
        """Opção 2: Cadastrar novo adotante."""
        print("\n" + "="*60)
        print("👤 CADASTRO DE ADOTANTE")
        print("="*60)
        
        try:
            nome = input("Nome completo: ").strip()
            if not nome:
                print("❌ Nome é obrigatório!")
                return
            
            idade = int(input("Idade: "))
            
            moradia = input("Tipo de moradia (casa/apartamento): ").strip().lower()
            if moradia not in ("casa", "apartamento"):
                print("❌ Moradia deve ser 'casa' ou 'apartamento'")
                return
            
            area_util = int(input("Área útil (m²): "))
            
            experiencia = input("Tem experiência com pets? (S/N): ").strip().upper() == "S"
            criancas = input("Tem crianças em casa? (S/N): ").strip().upper() == "S"
            outros_animais = input("Tem outros animais? (S/N): ").strip().upper() == "S"
            
            adotante = Adotante(
                nome=nome,
                idade=idade,
                moradia=moradia,
                area_util=area_util,
                experiencia=experiencia,
                criancas=criancas,
                outros_animais=outros_animais,
            )
            
            self.adotante_repo.add(adotante)
            self.adotante_repo.save()
            
            logger.log("ADOTANTE_CADASTRADO",
                       nome=adotante.nome,
                       idade=adotante.idade,
                       moradia=adotante.moradia,
                       area_util=adotante.area_util)
            
            print(f"\n✅ Adotante cadastrado com sucesso!")
            print(f"   {adotante}")
            
        except ValueError as e:
            print(f"❌ Erro de validação: {e}")
            logger.log("ERRO_CADASTRO_ADOTANTE", erro=str(e), tipo="ValidationError")
        except Exception as e:
            print(f"❌ Erro ao cadastrar: {e}")
            logger.log("ERRO_CADASTRO_ADOTANTE", erro=str(e), tipo=type(e).__name__)
    
    def _reservar(self):
        """Opção 3: Reservar um animal."""
        print("\n" + "="*60)
        print("🤩 RESERVA DE ANIMAL")
        print("="*60)
        
        # Lista animais disponíveis
        disponiveis = self.animal_repo.list(status=AnimalStatus.DISPONIVEL)
        
        if not disponiveis:
            print("\n⚠️  Nenhum animal disponível para reserva no momento.")
            logger.log("RESERVA_SEM_ANIMAIS")
            return
        
        print("\n📋 Animais disponíveis:")
        for i, animal in enumerate(disponiveis, 1):
            print(f"   [{i}] {animal.nome} - {animal.especie}/{animal.raca} - Porte {animal.porte}")
        
        try:
            escolha = int(input("\nEscolha o número do animal: ")) - 1
            if escolha < 0 or escolha >= len(disponiveis):
                print("❌ Escolha inválida!")
                return
            
            animal = disponiveis[escolha]
            
            # Lista adotantes
            adotantes = list(self.adotante_repo)
            if not adotantes:
                print("\n⚠️  Nenhum adotante cadastrado! Cadastre primeiro (opção 2).")
                logger.log("RESERVA_SEM_ADOTANTES")
                return
            
            print("\n📋 Adotantes cadastrados:")
            for i, adotante in enumerate(adotantes, 1):
                print(f"   [{i}] {adotante.nome} - {adotante.idade} anos")
            
            escolha_adotante = int(input("\nEscolha o número do adotante: ")) - 1
            if escolha_adotante < 0 or escolha_adotante >= len(adotantes):
                print("❌ Escolha inválida!")
                return
            
            adotante = adotantes[escolha_adotante]
            
            # Valida elegibilidade
            try:
                score = self.triagem_service.avaliar(adotante, animal)
                print(f"\n✅ Adotante elegível! Score de compatibilidade: {score}%")
                
                logger.log("TRIAGEM_APROVADA",
                           animal_id=animal.id,
                           animal_nome=animal.nome,
                           adotante=adotante.nome,
                           score=score)
                
            except PoliticaNaoAtendidaError as e:
                print(f"\n❌ Adotante não elegível: {e}")
                
                logger.log("TRIAGEM_REPROVADA",
                           animal_id=animal.id,
                           animal_nome=animal.nome,
                           adotante=adotante.nome,
                           motivo=str(e))
                
                # Pergunta se quer entrar na fila
                entrar_fila = input("\nDeseja entrar na fila de espera? (S/N): ").strip().upper()
                if entrar_fila == "S":
                    # Pega ou cria fila
                    fila = self.fila_repo.get_or_create(animal.id)
                    
                    # Calcula score mesmo com política não atendida (para priorização)
                    score_fila = self.triagem_service.compatibilidade.calcular(adotante, animal)
                    fila.adicionar(adotante, score_fila)
                    
                    # Salva fila
                    self.fila_repo.update(animal.id, fila)
                    self.fila_repo.save()
                    
                    logger.log("FILA_ADICIONADO",
                               animal_id=animal.id,
                               animal_nome=animal.nome,
                               adotante=adotante.nome,
                               score=score_fila,
                               posicao=len(fila))
                    
                    print(f"✅ {adotante.nome} adicionado à fila de espera com {score_fila} pontos")
                
                return
            
            # Faz a reserva
            self.reserva_service.reservar(animal.id, adotante.nome)
            
            logger.log("RESERVA_REALIZADA",
                       animal_id=animal.id,
                       animal_nome=animal.nome,
                       adotante=adotante.nome,
                       score=score,
                       validade=animal.reserva_ate)
            
            print(f"\n✅ Reserva realizada com sucesso para {adotante.nome}!")
            
        except ValueError as e:
            print(f"❌ Entrada inválida: {e}")
            logger.log("ERRO_RESERVA", erro=str(e), tipo="ValueError")
        except Exception as e:
            print(f"❌ Erro ao reservar: {e}")
            logger.log("ERRO_RESERVA", erro=str(e), tipo=type(e).__name__)
    
    def _adocao_efetiva(self):
        """Opção 4: Efetivar adoção de animal reservado."""
        print("\n" + "="*60)
        print("😁 ADOÇÃO EFETIVA")
        print("="*60)
        
        # Lista animais reservados
        reservados = self.animal_repo.list(status=AnimalStatus.RESERVADO)
        
        if not reservados:
            print("\n⚠️  Nenhum animal reservado no momento.")
            logger.log("ADOCAO_SEM_RESERVAS")
            return
        
        print("\n📋 Animais reservados:")
        for i, animal in enumerate(reservados, 1):
            print(f"   [{i}] {animal.nome} - Reservado por: {animal.reservado_por}")
        
        try:
            escolha = int(input("\nEscolha o número do animal: ")) - 1
            if escolha < 0 or escolha >= len(reservados):
                print("❌ Escolha inválida!")
                return
            
            animal = reservados[escolha]
            adotante_nome = animal.reservado_por
            
            # Escolhe estratégia de taxa
            print("\n💰 Estratégias de taxa disponíveis:")
            print("   [1] Padrão (R$ 100,00)")
            print("   [2] Sênior - Desconto 50% (animais > 8 anos)")
            print("   [3] Filhote - Acréscimo vacinas (animais < 1 ano)")
            print("   [4] Especial - Cuidados especiais (+ R$ 80,00)")
            
            estrategia_opcao = input("Escolha a estratégia (1-4): ").strip()
            
            strategies = {
                "1": TaxaPadrao(),
                "2": TaxaSenior(),
                "3": TaxaFilhote(),
                "4": TaxaEspecial(),
            }
            
            strategy = strategies.get(estrategia_opcao, TaxaPadrao())
            taxa_valor = strategy.calcular(animal)
            
            # Efetiva adoção
            contrato = self.adocao_service.adotar(
                animal_id=animal.id,
                adotante_nome=adotante_nome,
                strategy=strategy,
            )
            
            logger.log("ADOCAO_EFETIVADA",
                       animal_id=animal.id,
                       animal_nome=animal.nome,
                       adotante=adotante_nome,
                       taxa_tipo=strategy.nome(),
                       taxa_valor=taxa_valor)
            
            print("\n✅ ADOÇÃO REALIZADA COM SUCESSO!\n")
            print(contrato)
            
        except ValueError as e:
            print(f"❌ Erro: {e}")
            logger.log("ERRO_ADOCAO", erro=str(e), tipo="ValueError")
        except Exception as e:
            print(f"❌ Erro ao efetivar adoção: {e}")
            logger.log("ERRO_ADOCAO", erro=str(e), tipo=type(e).__name__)
    
    def _devolucao(self):
        """Opção 5: Processar devolução de animal adotado."""
        print("\n" + "="*60)
        print("😿 DEVOLUÇÃO DE ANIMAL")
        print("="*60)
        
        # Lista animais adotados
        adotados = self.animal_repo.list(status=AnimalStatus.ADOTADO)
        
        if not adotados:
            print("\n⚠️  Nenhum animal adotado no momento.")
            logger.log("DEVOLUCAO_SEM_ADOTADOS")
            return
        
        print("\n📋 Animais adotados:")
        for i, animal in enumerate(adotados, 1):
            print(f"   [{i}] {animal.nome} - {animal.especie}/{animal.raca}")
        
        try:
            escolha = int(input("\nEscolha o número do animal: ")) - 1
            if escolha < 0 or escolha >= len(adotados):
                print("❌ Escolha inválida!")
                return
            
            animal = adotados[escolha]
            
            motivo = input("\nMotivo da devolução: ").strip()
            if not motivo:
                print("❌ Motivo é obrigatório!")
                return
            
            problema = input("Há problema de saúde/comportamento? (S/N): ").strip().upper() == "S"
            
            # Processa devolução
            self.gestao_service.processar_devolucao(
                animal=animal,
                motivo=motivo,
                problema_saude_comportamento=problema,
            )
            
            # Salva alterações
            self.animal_repo.update(animal)
            self.animal_repo.save()
            
            logger.log("DEVOLUCAO_PROCESSADA",
                       animal_id=animal.id,
                       animal_nome=animal.nome,
                       motivo=motivo,
                       problema=problema,
                       novo_status=animal.status.value)
            
            print(f"\n✅ Devolução processada. Status atual: {animal.status.value}")
            
        except ValueError as e:
            print(f"❌ Erro: {e}")
            logger.log("ERRO_DEVOLUCAO", erro=str(e), tipo="ValueError")
        except TransicaoDeEstadoInvalidaError as e:
            print(f"❌ Transição inválida: {e}")
            logger.log("ERRO_DEVOLUCAO", erro=str(e), tipo="TransicaoInvalida")
        except Exception as e:
            print(f"❌ Erro ao processar devolução: {e}")
            logger.log("ERRO_DEVOLUCAO", erro=str(e), tipo=type(e).__name__)
    
    def _top_5(self):
        """Opção 6: Mostrar top 5 animais mais adotáveis."""
        print("\n" + "="*60)
        print("🔥 TOP 5 ANIMAIS MAIS ADOTÁVEIS")
        print("="*60)
        
        adotantes = list(self.adotante_repo)
        if not adotantes:
            print("\n⚠️  Nenhum adotante cadastrado para calcular compatibilidade.")
            logger.log("TOP5_SEM_ADOTANTES")
            return
        
        animais = self.animal_repo.list(status=AnimalStatus.DISPONIVEL)
        
        if not animais:
            print("\n⚠️  Nenhum animal disponível.")
            logger.log("TOP5_SEM_ANIMAIS")
            return
        
        try:
            top = self.relatorio_service.top_animais_adotaveis(
                animais=animais,
                adotantes=adotantes,
                limite=5,
            )
            
            if not top:
                print("\n⚠️  Não foi possível calcular o ranking.")
                return
            
            logger.log("RELATORIO_TOP5_GERADO", total_animais=len(top))
            
            print("\n🏆 Ranking de Compatibilidade:\n")
            for i, (animal, score) in enumerate(top, 1):
                print(f"   {i}º - {animal.nome} ({animal.especie}/{animal.porte}) - {score:.2f}% de compatibilidade média")
            
        except Exception as e:
            print(f"❌ Erro ao gerar ranking: {e}")
            logger.log("ERRO_TOP5", erro=str(e), tipo=type(e).__name__)
    
    def _taxa_adocao_especie_porte(self):
        """Opção 7: Relatório de taxa de adoções por espécie e porte."""
        print("\n" + "="*60)
        print("📊 TAXA DE ADOÇÕES POR ESPÉCIE/PORTE")
        print("="*60)
        
        adotados = self.animal_repo.list(status=AnimalStatus.ADOTADO)
        
        if not adotados:
            print("\n⚠️  Nenhum animal adotado ainda.")
            logger.log("RELATORIO_TAXA_SEM_DADOS")
            return
        
        try:
            resultado = self.relatorio_service.taxa_adocoes_por_especie_porte(adotados)
            
            logger.log("RELATORIO_TAXA_GERADO", total_adocoes=len(adotados))
            
            print("\n📈 Estatísticas de Adoções:\n")
            for (especie, porte), qtd in sorted(resultado.items()):
                print(f"   {especie} - Porte {porte}: {qtd} adoções")
            
            print(f"\n   TOTAL: {len(adotados)} adoções")
            
        except Exception as e:
            print(f"❌ Erro ao gerar relatório: {e}")
            logger.log("ERRO_RELATORIO_TAXA", erro=str(e), tipo=type(e).__name__)
    
    def _tempo_medio_adocao(self):
        """Opção 8: Relatório de tempo médio entre entrada e adoção."""
        print("\n" + "="*60)
        print("⏱️  TEMPO MÉDIO ENTRE ENTRADA E ADOÇÃO")
        print("="*60)
        
        try:
            todos_animais = list(self.animal_repo)
            tempo = self.relatorio_service.tempo_medio_entrada_adocao(todos_animais)
            
            if tempo is None:
                print("\n⚠️  Dados insuficientes para calcular tempo médio.")
                logger.log("RELATORIO_TEMPO_SEM_DADOS")
                return
            
            dias = tempo.days
            horas = tempo.seconds // 3600
            
            logger.log("RELATORIO_TEMPO_GERADO", dias=dias, horas=horas)
            
            print(f"\n⏳ Tempo médio: {dias} dias e {horas} horas")
            
        except Exception as e:
            print(f"❌ Erro ao calcular tempo médio: {e}")
            logger.log("ERRO_RELATORIO_TEMPO", erro=str(e), tipo=type(e).__name__)
    
    def _devolucoes_por_motivo(self):
        """Opção 9: Relatório de devoluções agrupadas por motivo."""
        print("\n" + "="*60)
        print("📋 DEVOLUÇÕES POR MOTIVO")
        print("="*60)
        
        try:
            todos_animais = list(self.animal_repo)
            resultado = self.relatorio_service.devolucoes_por_motivo(todos_animais)
            
            if not resultado:
                print("\n⚠️  Nenhuma devolução registrada.")
                logger.log("RELATORIO_DEVOLUCOES_SEM_DADOS")
                return
            
            total_devolucoes = sum(resultado.values())
            logger.log("RELATORIO_DEVOLUCOES_GERADO", total=total_devolucoes)
            
            print("\n📉 Motivos de Devolução:\n")
            for motivo, qtd in sorted(resultado.items(), key=lambda x: x[1], reverse=True):
                print(f"   • {motivo}: {qtd} devoluções")
            
            print(f"\n   TOTAL: {total_devolucoes} devoluções")
            
        except Exception as e:
            print(f"❌ Erro ao gerar relatório: {e}")
            logger.log("ERRO_RELATORIO_DEVOLUCOES", erro=str(e), tipo=type(e).__name__)
    
    def _reavaliar_animal(self):
        """Opção 10: Reavaliar animal em quarentena ou devolvido."""
        print("\n" + "="*60)
        print("🩺 REAVALIAÇÃO DE ANIMAL")
        print("="*60)
        
        # Lista animais em quarentena ou devolvidos
        em_avaliacao = [
            a for a in self.animal_repo 
            if a.status in (AnimalStatus.QUARENTENA, AnimalStatus.DEVOLVIDO)
        ]
        
        if not em_avaliacao:
            print("\n⚠️  Nenhum animal em quarentena ou devolvido.")
            logger.log("REAVALIACAO_SEM_ANIMAIS")
            return
        
        print("\n📋 Animais para reavaliação:")
        for i, animal in enumerate(em_avaliacao, 1):
            print(f"   [{i}] {animal.nome} - Status: {animal.status.value}")
        
        try:
            escolha = int(input("\nEscolha o número do animal: ")) - 1
            if escolha < 0 or escolha >= len(em_avaliacao):
                print("❌ Escolha inválida!")
                return
            
            animal = em_avaliacao[escolha]
            
            apto = input("\nAnimal está apto para adoção? (S/N): ").strip().upper() == "S"
            
            # Reavalia
            self.gestao_service.reavaliar_quarentena(animal, apto)
            
            # Salva alterações
            self.animal_repo.update(animal)
            self.animal_repo.save()
            
            logger.log("REAVALIACAO_CONCLUIDA",
                       animal_id=animal.id,
                       animal_nome=animal.nome,
                       apto=apto,
                       novo_status=animal.status.value)
            
            print(f"\n✅ Reavaliação concluída. Novo status: {animal.status.value}")
            
        except ValueError as e:
            print(f"❌ Erro: {e}")
            logger.log("ERRO_REAVALIACAO", erro=str(e), tipo="ValueError")
        except TransicaoDeEstadoInvalidaError as e:
            print(f"❌ Transição inválida: {e}")
            logger.log("ERRO_REAVALIACAO", erro=str(e), tipo="TransicaoInvalida")
        except Exception as e:
            print(f"❌ Erro ao reavaliar: {e}")
            logger.log("ERRO_REAVALIACAO", erro=str(e), tipo=type(e).__name__)
    
    def _simular_expiracao(self):
        """Opção 11: Simular expiração de reservas."""
        print("\n" + "="*60)
        print("⏳ SIMULAÇÃO DE EXPIRAÇÃO DE RESERVAS")
        print("="*60)
        
        try:
            # Guarda os IDs das reservas antes de expirar
            reservados_antes = [a.id for a in self.animal_repo.list(status=AnimalStatus.RESERVADO)]
            
            print("\n🔄 Executando job de expiração...")
            total = self.expiracao_job.executar()
            
            logger.log("EXPIRACAO_EXECUTADA", reservas_expiradas=total)
            
            if total == 0:
                print("\n✅ Nenhuma reserva expirada.")
            else:
                print(f"\n✅ {total} reserva(s) expirada(s) com sucesso!")
                
                # Para cada reserva expirada, verifica fila de espera
                for animal_id in reservados_antes:
                    animal = self.animal_repo.get(animal_id)
                    if animal and animal.status == AnimalStatus.DISPONIVEL:
                        fila = self.fila_repo.get(animal_id)
                        if fila and len(fila) > 0:
                            try:
                                proximo = fila.proximo()
                                # Salva a fila atualizada
                                self.fila_repo.update(animal_id, fila)
                                self.fila_repo.save()
                                
                                logger.log("FILA_NOTIFICADO",
                                           animal_id=animal_id,
                                           animal_nome=animal.nome,
                                           adotante=proximo.nome)
                                
                                print(f"\n📢 NOTIFICAÇÃO: {proximo.nome}, o animal {animal.nome} está disponível!")
                            except FilaVaziaError:
                                pass
            
        except Exception as e:
            print(f"❌ Erro ao executar job: {e}")
            logger.log("ERRO_EXPIRACAO", erro=str(e), tipo=type(e).__name__)
    
    def _ver_fila_espera(self):
        """Opção 12: Ver filas de espera atuais."""
        print("\n" + "="*60)
        print("👀 FILAS DE ESPERA ATUAIS")
        print("="*60)
        
        filas = self.fila_repo.list_all()
        
        if not filas:
            print("\n⚠️  Nenhuma fila de espera ativa.")
            logger.log("FILAS_VAZIA")
            return
        
        logger.log("FILAS_CONSULTADAS", total_filas=len(filas))
        
        print("\n📋 Filas ativas:\n")
        for animal_id, fila in filas.items():
            try:
                animal = self.animal_repo.get(animal_id)
                if animal:
                    print(f"   • {animal.nome} ({animal.especie}): {len(fila)} interessados")
                    if len(fila) > 0:
                        proximo = fila.espiar_proximo()
                        if proximo:
                            print(f"     → Próximo: {proximo.nome}")
            except Exception as e:
                print(f"   ⚠️  Erro ao processar fila {animal_id}: {e}")
                logger.log("ERRO_PROCESSAR_FILA", animal_id=animal_id, erro=str(e))
    
    def _sair(self):
        """Salva dados e encerra o sistema."""
        print("\n" + "="*60)
        print("🚪 ENCERRANDO SISTEMA")
        print("="*60)
        
        try:
            self.animal_repo.save()
            self.adotante_repo.save()
            self.fila_repo.save()
            
            logger.log("SISTEMA_ENCERRADO",
                       animais_salvos=len(self.animal_repo),
                       adotantes_salvos=len(self.adotante_repo),
                       filas_salvas=len(self.fila_repo))
            
            print("\n✅ Dados salvos com sucesso!")
            print("👋 Até logo!\n")
        except Exception as e:
            logger.log("ERRO_AO_SALVAR", erro=str(e), tipo=type(e).__name__)
            print(f"\n⚠️  Erro ao salvar dados: {e}")
            print("👋 Encerrando mesmo assim...\n")


# ============================================================================
# PONTO DE ENTRADA
# ============================================================================

def main():
    """Função principal - inicializa e executa o sistema."""
    try:
        sistema = SistemaAdocao()
        sistema.executar()
    except Exception as e:
        print(f"\n❌ Erro fatal ao inicializar sistema: {e}")
        logger.log("ERRO_FATAL", erro=str(e), tipo=type(e).__name__)
        sys.exit(1)


if __name__ == "__main__":
    main()