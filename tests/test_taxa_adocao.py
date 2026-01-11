"""
Testes para estratégias de cálculo de taxa de adoção.
"""

import pytest
from unittest.mock import Mock

from src.services.taxa_adocao import (
    TaxaPadrao,
    TaxaSenior,
    TaxaFilhote,
    TaxaEspecial,
)


@pytest.fixture
def animal_mock():
    """Cria um mock de Animal para testes."""
    return Mock()


class TestTaxaPadrao:
    """Testes para TaxaPadrao."""
    
    def test_calcular_valor_padrao(self, animal_mock):
        """Deve retornar valor base padrão de R$ 100,00."""
        estrategia = TaxaPadrao()
        taxa = estrategia.calcular(animal_mock)
        
        assert taxa == 100.0
    
    def test_calcular_valor_customizado(self, animal_mock):
        """Deve retornar valor base customizado."""
        estrategia = TaxaPadrao(valor_base=120.0)
        taxa = estrategia.calcular(animal_mock)
        
        assert taxa == 120.0
    
    def test_nome_estrategia(self):
        """Deve retornar nome correto da estratégia."""
        estrategia = TaxaPadrao()
        
        assert estrategia.nome() == "Padrão"


class TestTaxaSenior:
    """Testes para TaxaSenior."""
    
    def test_calcular_com_desconto_animal_senior(self, animal_mock):
        """Deve aplicar desconto de 50% para animal sênior (96+ meses)."""
        animal_mock.idade_meses = 100
        estrategia = TaxaSenior()
        taxa = estrategia.calcular(animal_mock)
        
        assert taxa == 50.0  # 100 * (1 - 0.5)
    
    def test_calcular_sem_desconto_animal_jovem(self, animal_mock):
        """Não deve aplicar desconto para animal jovem (< 96 meses)."""
        animal_mock.idade_meses = 50
        estrategia = TaxaSenior()
        taxa = estrategia.calcular(animal_mock)
        
        assert taxa == 100.0
    
    def test_calcular_limite_exato_senior(self, animal_mock):
        """Deve aplicar desconto quando idade == limite sênior."""
        animal_mock.idade_meses = 96
        estrategia = TaxaSenior()
        taxa = estrategia.calcular(animal_mock)
        
        assert taxa == 50.0
    
    def test_calcular_com_parametros_customizados(self, animal_mock):
        """Deve calcular com desconto e valor base customizados."""
        animal_mock.idade_meses = 100
        estrategia = TaxaSenior(
            valor_base=200.0,
            desconto_percentual=0.3,
            senior_a_partir_meses=84
        )
        taxa = estrategia.calcular(animal_mock)
        
        assert taxa == 140.0  # 200 * (1 - 0.3)
    
    def test_nome_estrategia(self):
        """Deve retornar nome com percentual de desconto."""
        estrategia = TaxaSenior()
        
        assert estrategia.nome() == "Sênior (50% desconto)"


class TestTaxaFilhote:
    """Testes para TaxaFilhote."""
    
    def test_calcular_com_acrescimo_filhote(self, animal_mock):
        """Deve adicionar valor de vacinas para filhote (<= 12 meses)."""
        animal_mock.idade_meses = 8
        estrategia = TaxaFilhote()
        taxa = estrategia.calcular(animal_mock)
        
        assert taxa == 150.0  # 100 + 50
    
    def test_calcular_sem_acrescimo_adulto(self, animal_mock):
        """Não deve adicionar vacinas para animal adulto (> 12 meses)."""
        animal_mock.idade_meses = 24
        estrategia = TaxaFilhote()
        taxa = estrategia.calcular(animal_mock)
        
        assert taxa == 100.0
    
    def test_calcular_limite_exato_filhote(self, animal_mock):
        """Deve aplicar acréscimo quando idade == limite filhote."""
        animal_mock.idade_meses = 12
        estrategia = TaxaFilhote()
        taxa = estrategia.calcular(animal_mock)
        
        assert taxa == 150.0
    
    def test_calcular_com_parametros_customizados(self, animal_mock):
        """Deve calcular com acréscimo e valor base customizados."""
        animal_mock.idade_meses = 6
        estrategia = TaxaFilhote(
            valor_base=120.0,
            acrescimo_vacinas=70.0,
            filhote_ate_meses=18
        )
        taxa = estrategia.calcular(animal_mock)
        
        assert taxa == 190.0  # 120 + 70
    
    def test_nome_estrategia(self):
        """Deve retornar nome indicando inclusão de vacinas."""
        estrategia = TaxaFilhote()
        
        assert estrategia.nome() == "Filhote (inclui vacinas)"


class TestTaxaEspecial:
    """Testes para TaxaEspecial."""
    
    def test_calcular_sempre_com_acrescimo(self, animal_mock):
        """Deve sempre adicionar valor de tratamento especial."""
        estrategia = TaxaEspecial()
        taxa = estrategia.calcular(animal_mock)
        
        assert taxa == 180.0  # 100 + 80
    
    def test_calcular_com_parametros_customizados(self, animal_mock):
        """Deve calcular com acréscimo e valor base customizados."""
        estrategia = TaxaEspecial(
            valor_base=150.0,
            acrescimo_tratamento=100.0
        )
        taxa = estrategia.calcular(animal_mock)
        
        assert taxa == 250.0  # 150 + 100
    
    def test_nome_estrategia(self):
        """Deve retornar nome indicando cuidados especiais."""
        estrategia = TaxaEspecial()
        
        assert estrategia.nome() == "Especial (cuidados especiais)"


class TestIntegracaoEstrategias:
    """Testes de integração entre diferentes estratégias."""
    
    def test_comparacao_valores_diferentes_estrategias(self, animal_mock):
        """Deve calcular valores diferentes para cada estratégia."""
        animal_mock.idade_meses = 50  # Nem filhote, nem sênior
        
        padrao = TaxaPadrao()
        senior = TaxaSenior()
        filhote = TaxaFilhote()
        especial = TaxaEspecial()
        
        assert padrao.calcular(animal_mock) == 100.0
        assert senior.calcular(animal_mock) == 100.0
        assert filhote.calcular(animal_mock) == 100.0
        assert especial.calcular(animal_mock) == 180.0
    
    def test_todas_estrategias_retornam_float(self, animal_mock):
        """Todas as estratégias devem retornar float."""
        animal_mock.idade_meses = 50
        estrategias = [
            TaxaPadrao(),
            TaxaSenior(),
            TaxaFilhote(),
            TaxaEspecial(),
        ]
        
        for estrategia in estrategias:
            taxa = estrategia.calcular(animal_mock)
            assert isinstance(taxa, float)
    
    def test_imutabilidade_estrategias(self):
        """Estratégias devem ser imutáveis (frozen dataclass)."""
        estrategia = TaxaPadrao()
        
        with pytest.raises(Exception):  # FrozenInstanceError
            estrategia.valor_base = 200.0

