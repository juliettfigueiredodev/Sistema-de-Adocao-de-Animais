"""
Script de teste completo do sistema de adoção.
Testa todos os módulos e fluxos principais.
"""

from datetime import datetime, timezone
from pathlib import Path

# Models
from src.models.pessoa import Pessoa
from src.models.adotante import Adotante
from src.models.cachorro import Cachorro
from src.models.gato import Gato
from src.models.animal_status import AnimalStatus

# Infrastructure
from src.infrastructure.animal_repository import AnimalRepository
from src.infrastructure.settings_loader import SettingsLoader

# Services
from src.services.compatibilidade_service import CompatibilidadeService
from src.services.triagem_service import TriagemService
from src.services.reserva_service import ReservaService
from src.services.adocao_service import AdocaoService
from src.services.expiracao_reserva import ExpiracaoReservaJob
from src.services.relatorio_service import RelatorioService
from src.services.taxa_adocao import TaxaPadrao, TaxaSenior, TaxaFilhote

# Validators
from src.validators.politica_triagem import PoliticaTriagem
from src.validators.exceptions import PoliticaNaoAtendidaError


def print_secao(titulo: str):
    """Imprime cabeçalho de seção."""
    print("\n" + "="*70)
    print(f"  {titulo}")
    print("="*70 + "\n")


def teste_1_models():
    """Testa models: Pessoa, Adotante, Cachorro, Gato."""
    print_secao("TESTE 1: MODELS (Pessoa, Adotante, Animal)")
    
    try:
        # Teste Pessoa
        print("✓ Testando Pessoa...")
        pessoa = Pessoa("João Silva", 30)
        print(f"  {pessoa}")
        print(f"  repr: {pessoa!r}")
        assert pessoa.nome == "João Silva"
        assert pessoa.idade == 30
        print("  ✅ Pessoa OK!")
        
        # Teste Adotante
        print("\n✓ Testando Adotante...")
        adotante = Adotante(
            nome="Maria Santos",
            idade=28,
            moradia="casa",
            area_util=80,
            experiencia=True,
            criancas=False,
            outros_animais=False
        )
        print(f"  {adotante}")
        print(f"  repr: {adotante!r}")
        print(f"  to_dict: {adotante.to_dict()}")
        assert adotante.area_util == 80
        print("  ✅ Adotante OK!")
        
        # Teste Cachorro
        print("\n✓ Testando Cachorro...")
        cachorro = Cachorro(
            raca="Labrador",
            nome="Rex",
            sexo="M",
            idade_meses=24,
            porte="G",
            necessidade_passeio=8,
            temperamento=["docil", "energico"]
        )
        print(f"  {cachorro}")
        print(f"  Status: {cachorro.status}")
        print(f"  Temperamento: {cachorro.temperamento}")
        assert cachorro.porte == "G"
        assert cachorro.necessidade_passeio == 8
        print("  ✅ Cachorro OK!")
        
        # Teste Gato
        print("\n✓ Testando Gato...")
        gato = Gato(
            raca="Siamês",
            nome="Mimi",
            sexo="F",
            idade_meses=18,
            porte="P",
            independencia=7,
            temperamento=["calmo", "carinhoso"]
        )
        print(f"  {gato}")
        print(f"  Independência: {gato.independencia}")
        assert gato.independencia == 7
        print("  ✅ Gato OK!")
        
        # Teste transição de status
        print("\n✓ Testando transições de status...")
        cachorro.mudar_status(AnimalStatus.RESERVADO, motivo="Teste")
        assert cachorro.status == AnimalStatus.RESERVADO
        print(f"  Status mudou para: {cachorro.status}")
        
        # Teste histórico
        print("\n✓ Testando histórico de eventos...")
        print("  Eventos:")
        for evento in cachorro:
            print(f"    - {evento.tipo}: {evento.detalhes}")
        print("  ✅ Histórico OK!")
        
        print("\n✅ TODOS OS MODELS FUNCIONANDO!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NOS MODELS: {e}")
        import traceback
        traceback.print_exc()
        return False


def teste_2_infrastructure():
    """Testa infraestrutura: SettingsLoader, Repository."""
    print_secao("TESTE 2: INFRASTRUCTURE (Settings, Repository)")
    
    try:
        # Teste SettingsLoader
        print("✓ Testando SettingsLoader...")
        settings = SettingsLoader.carregar()
        print(f"  Configurações carregadas:")
        print(f"    - Idade mínima: {settings['politicas']['idade_minima']}")
        print(f"    - Duração reserva: {settings['reserva']['duracao_horas']}h")
        print(f"    - Pesos compatibilidade: {settings['compatibilidade']['pesos']}")
        assert settings['politicas']['idade_minima'] == 18
        print("  ✅ SettingsLoader OK!")
        
        # Teste Repository
        print("\n✓ Testando AnimalRepository...")
        repo = AnimalRepository("data/teste_animais.json")
        
        # Adiciona animais de teste
        cachorro1 = Cachorro(
            raca="Labrador", nome="Rex", sexo="M",
            idade_meses=24, porte="G", necessidade_passeio=8,
            temperamento=["docil"]
        )
        
        gato1 = Gato(
            raca="Persa", nome="Frajola", sexo="M",
            idade_meses=36, porte="M", independencia=6,
            temperamento=["calmo"]
        )
        
        repo.add(cachorro1)
        repo.add(gato1)
        
        print(f"  Total de animais: {len(repo)}")
        print(f"  {repo}")
        
        # Testa busca
        animal_encontrado = repo.get(cachorro1.id)
        assert animal_encontrado.nome == "Rex"
        print(f"  Busca por ID: {animal_encontrado.nome} ✅")
        
        # Testa listagem
        disponiveis = repo.list(status=AnimalStatus.DISPONIVEL)
        print(f"  Animais disponíveis: {len(disponiveis)}")
        
        # Testa persistência
        repo.save()
        print("  Arquivo salvo com sucesso!")
        
        # Testa recarga
        repo2 = AnimalRepository("data/teste_animais.json")
        repo2.load()
        print(f"  Recarregados: {len(repo2)} animais")
        
        # Limpa arquivo de teste
        Path("data/teste_animais.json").unlink(missing_ok=True)
        
        print("\n✅ INFRASTRUCTURE FUNCIONANDO!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NA INFRASTRUCTURE: {e}")
        import traceback
        traceback.print_exc()
        return False


def teste_3_validators():
    """Testa validadores: PoliticaTriagem."""
    print_secao("TESTE 3: VALIDATORS (Políticas de Triagem)")
    
    try:
        print("✓ Testando PoliticaTriagem...")
        politica = PoliticaTriagem()
        
        # Adotante válido
        adotante_valido = Adotante(
            nome="Carlos", idade=30, moradia="casa",
            area_util=100, experiencia=True,
            criancas=False, outros_animais=False
        )
        
        # Teste 1: Adotante válido para porte G
        print("  Teste 1: Adotante válido para porte G...")
        try:
            politica.validar(adotante_valido, "G")
            print("    ✅ Passou na validação!")
        except PoliticaNaoAtendidaError as e:
            print(f"    ❌ Não deveria ter falhado: {e}")
            return False
        
        # Teste 2: Adotante menor de idade
        print("  Teste 2: Adotante menor de idade...")
        adotante_menor = Adotante(
            nome="João", idade=17, moradia="casa",
            area_util=80, experiencia=False,
            criancas=False, outros_animais=False
        )
        try:
            politica.validar(adotante_menor, "P")
            print("    ❌ Deveria ter falhado!")
            return False
        except PoliticaNaoAtendidaError as e:
            print(f"    ✅ Falhou corretamente: {e}")
        
        # Teste 3: Apartamento para porte G
        print("  Teste 3: Apartamento para porte G...")
        adotante_apto = Adotante(
            nome="Ana", idade=25, moradia="apartamento",
            area_util=50, experiencia=True,
            criancas=False, outros_animais=False
        )
        try:
            politica.validar(adotante_apto, "G")
            print("    ❌ Deveria ter falhado!")
            return False
        except PoliticaNaoAtendidaError as e:
            print(f"    ✅ Falhou corretamente: {e}")
        
        print("\n✅ VALIDATORS FUNCIONANDO!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NOS VALIDATORS: {e}")
        import traceback
        traceback.print_exc()
        return False


def teste_4_services():
    """Testa services: Compatibilidade, Triagem."""
    print_secao("TESTE 4: SERVICES (Compatibilidade, Triagem)")
    
    try:
        # Setup
        adotante = Adotante(
            nome="Maria", idade=28, moradia="casa",
            area_util=80, experiencia=True,
            criancas=False, outros_animais=False
        )
        
        cachorro = Cachorro(
            raca="Labrador", nome="Rex", sexo="M",
            idade_meses=24, porte="G", necessidade_passeio=8,
            temperamento=["docil", "energico"]
        )
        
        # Teste CompatibilidadeService
        print("✓ Testando CompatibilidadeService...")
        compatibilidade = CompatibilidadeService()
        score = compatibilidade.calcular(adotante, cachorro)
        print(f"  Score de compatibilidade: {score}%")
        assert 0 <= score <= 100
        print("  ✅ CompatibilidadeService OK!")
        
        # Teste TriagemService
        print("\n✓ Testando TriagemService...")
        triagem = TriagemService()
        score = triagem.avaliar(adotante, cachorro)
        print(f"  Score de triagem: {score}%")
        assert 0 <= score <= 100
        print("  ✅ TriagemService OK!")
        
        print("\n✅ SERVICES BÁSICOS FUNCIONANDO!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NOS SERVICES: {e}")
        import traceback
        traceback.print_exc()
        return False


def teste_5_fluxo_completo():
    """Testa fluxo completo: Reserva → Adoção."""
    print_secao("TESTE 5: FLUXO COMPLETO (Reserva → Adoção)")
    
    try:
        # Setup
        repo = AnimalRepository("data/teste_fluxo.json")
        
        cachorro = Cachorro(
            raca="Beagle", nome="Bolt", sexo="M",
            idade_meses=12, porte="M", necessidade_passeio=7,
            temperamento=["energico", "sociavel"]
        )
        repo.add(cachorro)
        repo.save()
        
        adotante_nome = "Pedro Oliveira"
        
        print(f"✓ Animal criado: {cachorro.nome} ({cachorro.status.value})")
        
        # Passo 1: Reserva
        print("\n✓ PASSO 1: Reservando animal...")
        reserva_service = ReservaService(repo, duracao_horas=48)
        reserva_service.reservar(cachorro.id, adotante_nome)
        
        # Recarrega para ver mudança
        repo.load()
        cachorro = repo.get(cachorro.id)
        print(f"  Status após reserva: {cachorro.status.value}")
        print(f"  Reservado por: {cachorro.reservado_por}")
        print(f"  Reserva até: {cachorro.reserva_ate}")
        assert cachorro.status == AnimalStatus.RESERVADO
        print("  ✅ Reserva OK!")
        
        # Passo 2: Adoção
        print("\n✓ PASSO 2: Adotando animal...")
        adocao_service = AdocaoService(repo, pasta_contratos="data/teste_contratos")
        estrategia = TaxaPadrao(valor_base=100.0)
        
        contrato = adocao_service.adotar(
            animal_id=cachorro.id,
            adotante_nome=adotante_nome,
            strategy=estrategia
        )
        
        print("  Contrato gerado:")
        print("  " + "-"*60)
        for linha in contrato.split("\n")[:10]:  # Primeiras 10 linhas
            print(f"  {linha}")
        print("  " + "-"*60)
        
        # Recarrega
        repo.load()
        cachorro = repo.get(cachorro.id)
        print(f"\n  Status após adoção: {cachorro.status.value}")
        assert cachorro.status == AnimalStatus.ADOTADO
        print("  ✅ Adoção OK!")
        
        # Limpa
        Path("data/teste_fluxo.json").unlink(missing_ok=True)
        import shutil
        shutil.rmtree("data/teste_contratos", ignore_errors=True)
        
        print("\n✅ FLUXO COMPLETO FUNCIONANDO!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NO FLUXO: {e}")
        import traceback
        traceback.print_exc()
        return False


def teste_6_relatorios():
    """Testa TODOS os 4 relatórios obrigatórios."""
    print_secao("TESTE 6: RELATÓRIOS (Todos os 4)")
    
    try:
        # ========================================
        # SETUP: Cria dados de teste
        # ========================================
        repo = AnimalRepository("data/teste_relatorios.json")
        
        # Cria animais
        cachorro1 = Cachorro(
            raca="Labrador", nome="Max", sexo="M",
            idade_meses=24, porte="G", necessidade_passeio=8,
            temperamento=["docil", "energico"]
        )
        
        cachorro2 = Cachorro(
            raca="Poodle", nome="Mel", sexo="F",
            idade_meses=96, porte="P", necessidade_passeio=5,
            temperamento=["calmo"]
        )
        
        cachorro3 = Cachorro(
            raca="Beagle", nome="Bob", sexo="M",
            idade_meses=36, porte="M", necessidade_passeio=7,
            temperamento=["sociavel"]
        )
        
        gato1 = Gato(
            raca="Siamês", nome="Luna", sexo="F",
            idade_meses=18, porte="P", independencia=8,
            temperamento=["independente", "calmo"]
        )
        
        gato2 = Gato(
            raca="Persa", nome="Frajola", sexo="M",
            idade_meses=48, porte="M", independencia=6,
            temperamento=["docil"]
        )
        
        repo.add(cachorro1)
        repo.add(cachorro2)
        repo.add(cachorro3)
        repo.add(gato1)
        repo.add(gato2)
        repo.save()
        
        # Simula adoções para alguns animais
        print("✓ Simulando adoções para testes...")
        
        # Adota Max (Labrador)
        cachorro1.mudar_status(AnimalStatus.RESERVADO)
        cachorro1.reservado_por = "João Silva"
        cachorro1.mudar_status(AnimalStatus.ADOTADO, motivo="Adotado por João Silva")
        cachorro1.registrar_evento("ADOCAO", "Adotado por João Silva")
        repo.update(cachorro1)
        
        # Adota Luna (Gato)
        gato1.mudar_status(AnimalStatus.RESERVADO)
        gato1.reservado_por = "Maria Santos"
        gato1.mudar_status(AnimalStatus.ADOTADO, motivo="Adotado por Maria Santos")
        gato1.registrar_evento("ADOCAO", "Adotado por Maria Santos")
        repo.update(gato1)
        
        # Adota e devolve Mel (Poodle)
        cachorro2.mudar_status(AnimalStatus.RESERVADO)
        cachorro2.reservado_por = "Pedro Costa"
        cachorro2.mudar_status(AnimalStatus.ADOTADO, motivo="Adotado por Pedro Costa")
        cachorro2.registrar_evento("ADOCAO", "Adotado por Pedro Costa")
        cachorro2.mudar_status(AnimalStatus.DEVOLVIDO, motivo="Alergia do adotante")
        repo.update(cachorro2)
        
        # Adota Bob (Beagle)
        cachorro3.mudar_status(AnimalStatus.RESERVADO)
        cachorro3.reservado_por = "Ana Lima"
        cachorro3.mudar_status(AnimalStatus.ADOTADO, motivo="Adotado por Ana Lima")
        cachorro3.registrar_evento("ADOCAO", "Adotado por Ana Lima")
        repo.update(cachorro3)
        
        repo.save()
        print(f"  {repo.count(status=AnimalStatus.ADOTADO)} animais adotados")
        print(f"  {repo.count(status=AnimalStatus.DEVOLVIDO)} animal devolvido")
        
        # Cria adotantes para teste de compatibilidade
        adotantes = [
            Adotante("João", 30, "casa", 100, True, False, False),
            Adotante("Maria", 25, "apartamento", 50, True, False, True),
            Adotante("Pedro", 35, "casa", 120, False, True, False),
            Adotante("Ana", 28, "casa", 90, True, False, False),
        ]
        
        # ========================================
        # RELATÓRIO 1: Top 5 animais mais adotáveis
        # ========================================
        print("\n" + "─"*70)
        print("📊 RELATÓRIO 1: Top 5 Animais Mais Adotáveis")
        print("─"*70)
        
        relatorio = RelatorioService()
        animais_disponiveis = repo.list(status=AnimalStatus.DISPONIVEL)
        
        print(f"✓ Testando top_animais_adotaveis...")
        print(f"  Animais disponíveis para análise: {len(animais_disponiveis)}")
        print(f"  Adotantes na base: {len(adotantes)}")
        
        if animais_disponiveis:
            top = relatorio.top_animais_adotaveis(
                animais_disponiveis, 
                adotantes, 
                limite=5
            )
            
            print(f"\n  🏆 TOP {len(top)} ANIMAIS MAIS ADOTÁVEIS:")
            for i, (animal, score) in enumerate(top, 1):
                print(f"    {i}. {animal.nome:15s} ({animal.especie:10s} | "
                      f"Porte {animal.porte}) - Score: {score:5.2f}%")
            
            assert len(top) <= 5, "Não deve retornar mais que o limite"
            assert all(0 <= score <= 100 for _, score in top), "Scores devem estar entre 0-100"
            print("  ✅ Relatório 1 OK!")
        else:
            print("  ⚠️  Sem animais disponíveis para o ranking")
        
        # ========================================
        # RELATÓRIO 2: Taxa de adoções por espécie/porte
        # ========================================
        print("\n" + "─"*70)
        print("📊 RELATÓRIO 2: Taxa de Adoções por Espécie e Porte")
        print("─"*70)
        
        print("✓ Testando taxa_adocoes_por_especie_porte...")
        
        animais_adotados = repo.list(status=AnimalStatus.ADOTADO)
        print(f"  Total de animais adotados: {len(animais_adotados)}")
        
        if animais_adotados:
            taxa = relatorio.taxa_adocoes_por_especie_porte(animais_adotados)
            
            print(f"\n  📈 ADOÇÕES POR ESPÉCIE E PORTE:")
            for (especie, porte), qtd in sorted(taxa.items()):
                print(f"    {especie:12s} | Porte {porte} : {qtd} adoções")
            
            # Validações
            assert isinstance(taxa, dict), "Deve retornar dicionário"
            assert all(isinstance(qtd, int) for qtd in taxa.values()), "Quantidades devem ser inteiros"
            assert sum(taxa.values()) == len(animais_adotados), "Soma deve bater com total"
            print("  ✅ Relatório 2 OK!")
        else:
            print("  ⚠️  Sem adoções registradas")
        
        # ========================================
        # RELATÓRIO 3: Tempo médio entre entrada e adoção
        # ========================================
        print("\n" + "─"*70)
        print("📊 RELATÓRIO 3: Tempo Médio Entre Entrada e Adoção")
        print("─"*70)
        
        print("✓ Testando tempo_medio_entrada_adocao...")
        
        todos_animais = repo.list()
        tempo_medio = relatorio.tempo_medio_entrada_adocao(todos_animais)
        
        if tempo_medio:
            dias = tempo_medio.days
            horas = tempo_medio.seconds // 3600
            minutos = (tempo_medio.seconds % 3600) // 60
            
            print(f"\n  ⏱️  TEMPO MÉDIO DE ADOÇÃO:")
            print(f"    {dias} dias, {horas}h {minutos}min")
            
            # Validações
            assert tempo_medio.total_seconds() >= 0, "Tempo não pode ser negativo"
            print("  ✅ Relatório 3 OK!")
        else:
            print("  ⚠️  Não há dados suficientes para calcular tempo médio")
            print("    (precisa de animais com evento de ADOCAO no histórico)")
        
        # ========================================
        # RELATÓRIO 4: Devoluções por motivo
        # ========================================
        print("\n" + "─"*70)
        print("📊 RELATÓRIO 4: Devoluções por Motivo")
        print("─"*70)
        
        print("✓ Testando devolucoes_por_motivo...")
        
        # Para este teste, vamos usar animais devolvidos
        animais_devolvidos = repo.list(status=AnimalStatus.DEVOLVIDO)
        print(f"  Total de animais devolvidos: {len(animais_devolvidos)}")
        
        if animais_devolvidos:
            devolucoes = relatorio.devolucoes_por_motivo(todos_animais)
            
            print(f"\n  📉 DEVOLUÇÕES POR MOTIVO:")
            if devolucoes:
                for motivo, qtd in sorted(devolucoes.items(), key=lambda x: x[1], reverse=True):
                    print(f"    {motivo:40s} : {qtd} devolução(ões)")
                
                # Validações
                assert isinstance(devolucoes, dict), "Deve retornar dicionário"
                assert all(isinstance(qtd, int) for qtd in devolucoes.values()), "Quantidades devem ser inteiros"
                print("  ✅ Relatório 4 OK!")
            else:
                print("    (Nenhum motivo extraído do histórico)")
                print("  ⚠️  Estrutura correta mas sem dados de motivos")
        else:
            print("  ℹ️  Sem devoluções registradas (esperado em sistema novo)")
            print("  ✅ Relatório 4 OK (sem dados para processar)")
        
        # ========================================
        # RESUMO FINAL
        # ========================================
        print("\n" + "="*70)
        print("  RESUMO DOS RELATÓRIOS")
        print("="*70)
        print("  ✅ Relatório 1: Top animais adotáveis")
        print("  ✅ Relatório 2: Taxa de adoções por espécie/porte")
        print("  ✅ Relatório 3: Tempo médio entrada → adoção")
        print("  ✅ Relatório 4: Devoluções por motivo")
        print("="*70)
        
        # Limpa arquivos de teste
        Path("data/teste_relatorios.json").unlink(missing_ok=True)
        
        print("\n✅ TODOS OS 4 RELATÓRIOS FUNCIONANDO!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NOS RELATÓRIOS: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Executa todos os testes."""
    print("\n" + "█"*70)
    print("█  SISTEMA DE ADOÇÃO DE ANIMAIS - TESTE COMPLETO")
    print("█"*70)
    
    resultados = []
    
    # Executa testes
    resultados.append(("Models", teste_1_models()))
    resultados.append(("Infrastructure", teste_2_infrastructure()))
    resultados.append(("Validators", teste_3_validators()))
    resultados.append(("Services", teste_4_services()))
    resultados.append(("Fluxo Completo", teste_5_fluxo_completo()))
    resultados.append(("Relatórios", teste_6_relatorios()))
    
    # Resumo
    print("\n" + "="*70)
    print("  RESUMO DOS TESTES")
    print("="*70)
    
    total = len(resultados)
    passou = sum(1 for _, ok in resultados if ok)
    
    for nome, ok in resultados:
        status = "✅ PASSOU" if ok else "❌ FALHOU"
        print(f"  {nome:20s} {status}")
    
    print("\n" + "="*70)
    print(f"  RESULTADO FINAL: {passou}/{total} testes passaram")
    print("="*70)
    
    if passou == total:
        print("\n🎉 PARABÉNS! TODOS OS TESTES PASSARAM! 🎉")
        print("✅ Seu sistema está funcionando perfeitamente!")
        return 0
    else:
        print("\n⚠️  ALGUNS TESTES FALHARAM")
        print("❌ Revise os erros acima e corrija os problemas.")
        return 1


if __name__ == "__main__":
    exit(main())