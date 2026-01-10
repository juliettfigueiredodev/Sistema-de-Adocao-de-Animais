"""
Estratégias de cálculo de taxa de adoção (padrão Strategy).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.models.animal import Animal


class TaxaAdocaoStrategy(ABC):
    """
    Interface para estratégias de cálculo de taxa de adoção.
    
    Implementa o padrão de projeto Strategy para permitir
    diferentes formas de calcular a taxa de adoção.
    
    Example:
        >>> class MinhaEstrategia(TaxaAdocaoStrategy):
        ...     def calcular(self, animal: Animal) -> float:
        ...         return 150.0
        ...     def nome(self) -> str:
        ...         return "Minha Estratégia"
    """
    
    @abstractmethod
    def calcular(self, animal: Animal) -> float:
        """
        Calcula a taxa de adoção para um animal.
        
        Args:
            animal: Animal para o qual calcular a taxa.
        
        Returns:
            Valor da taxa em reais.
        """
        raise NotImplementedError

    @abstractmethod
    def nome(self) -> str:
        """
        Retorna o nome da estratégia.
        
        Returns:
            Nome descritivo da estratégia.
        """
        raise NotImplementedError


@dataclass(frozen=True)
class TaxaPadrao(TaxaAdocaoStrategy):
    """
    Estratégia de taxa padrão para todos os animais.
    
    Attributes:
        valor_base: Valor fixo da taxa (padrão: R$ 100,00).
    
    Example:
        >>> estrategia = TaxaPadrao(valor_base=120.0)
        >>> taxa = estrategia.calcular(animal)
        120.0
    """
    
    valor_base: float = 100.0

    def calcular(self, animal: Animal) -> float:
        """
        Retorna o valor base fixo.
        
        Args:
            animal: Animal (não utilizado nesta estratégia).
        
        Returns:
            Valor base da taxa.
        """
        return float(self.valor_base)

    def nome(self) -> str:
        """Nome da estratégia."""
        return "Padrão"


@dataclass(frozen=True)
class TaxaSenior(TaxaAdocaoStrategy):
    """
    Estratégia com desconto para animais idosos (sêniores).
    
    Aplica desconto percentual para animais acima de determinada idade,
    incentivando a adoção de animais mais velhos.
    
    Attributes:
        valor_base: Valor base da taxa (padrão: R$ 100,00).
        desconto_percentual: Desconto aplicado (0.0 a 1.0, padrão: 0.5 = 50%).
        senior_a_partir_meses: Idade mínima em meses para ser sênior (padrão: 96 = 8 anos).
    
    Example:
        >>> estrategia = TaxaSenior(
        ...     valor_base=100.0,
        ...     desconto_percentual=0.5,
        ...     senior_a_partir_meses=96
        ... )
        >>> # Animal com 100 meses: R$ 50,00 (50% de desconto)
        >>> # Animal com 50 meses: R$ 100,00 (sem desconto)
    """
    
    valor_base: float = 100.0
    desconto_percentual: float = 0.5  # 50%
    senior_a_partir_meses: int = 96   # 8 anos

    def calcular(self, animal: Animal) -> float:
        """
        Calcula taxa com desconto se animal for sênior.
        
        Args:
            animal: Animal para verificar idade.
        
        Returns:
            Taxa com ou sem desconto.
        """
        if animal.idade_meses >= self.senior_a_partir_meses:
            return float(self.valor_base) * (1.0 - self.desconto_percentual)
        return float(self.valor_base)

    def nome(self) -> str:
        """Nome da estratégia."""
        return f"Sênior ({int(self.desconto_percentual * 100)}% desconto)"


@dataclass(frozen=True)
class TaxaFilhote(TaxaAdocaoStrategy):
    """
    Estratégia com acréscimo para filhotes (custos de vacinas).
    
    Adiciona valor extra para cobrir custos de vacinas e cuidados
    iniciais de filhotes.
    
    Attributes:
        valor_base: Valor base da taxa (padrão: R$ 100,00).
        acrescimo_vacinas: Valor adicional para vacinas (padrão: R$ 50,00).
        filhote_ate_meses: Idade máxima em meses para ser filhote (padrão: 12 = 1 ano).
    
    Example:
        >>> estrategia = TaxaFilhote(
        ...     valor_base=100.0,
        ...     acrescimo_vacinas=50.0,
        ...     filhote_ate_meses=12
        ... )
        >>> # Animal com 8 meses: R$ 150,00
        >>> # Animal com 24 meses: R$ 100,00
    """
    
    valor_base: float = 100.0
    acrescimo_vacinas: float = 50.0
    filhote_ate_meses: int = 12

    def calcular(self, animal: Animal) -> float:
        """
        Calcula taxa com acréscimo se animal for filhote.
        
        Args:
            animal: Animal para verificar idade.
        
        Returns:
            Taxa com ou sem acréscimo.
        """
        if animal.idade_meses <= self.filhote_ate_meses:
            return float(self.valor_base) + float(self.acrescimo_vacinas)
        return float(self.valor_base)

    def nome(self) -> str:
        """Nome da estratégia."""
        return "Filhote (inclui vacinas)"


@dataclass(frozen=True)
class TaxaEspecial(TaxaAdocaoStrategy):
    """
    Estratégia com acréscimo para animais com necessidades especiais.
    
    Adiciona valor extra para cobrir custos de tratamentos contínuos
    ou cuidados especiais.
    
    Attributes:
        valor_base: Valor base da taxa (padrão: R$ 100,00).
        acrescimo_tratamento: Valor adicional para tratamento (padrão: R$ 80,00).
    
    Example:
        >>> estrategia = TaxaEspecial(
        ...     valor_base=100.0,
        ...     acrescimo_tratamento=80.0
        ... )
        >>> taxa = estrategia.calcular(animal)
        180.0
    """
    
    valor_base: float = 100.0
    acrescimo_tratamento: float = 80.0

    def calcular(self, animal: Animal) -> float:
        """
        Calcula taxa com acréscimo para cuidados especiais.
        
        Args:
            animal: Animal (sempre aplica acréscimo).
        
        Returns:
            Taxa com acréscimo.
        """
        return float(self.valor_base) + float(self.acrescimo_tratamento)

    def nome(self) -> str:
        """Nome da estratégia."""
        return "Especial (cuidados especiais)"