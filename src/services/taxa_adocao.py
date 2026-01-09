from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from models.animal import Animal


class TaxaAdocaoStrategy(ABC):
    @abstractmethod
    def calcular(self, animal: Animal) -> float:
        raise NotImplementedError

    @abstractmethod
    def nome(self) -> str:
        raise NotImplementedError


@dataclass(frozen=True)
class TaxaPadrao(TaxaAdocaoStrategy):
    valor_base: float = 100.0

    def calcular(self, animal: Animal) -> float:
        return float(self.valor_base)

    def nome(self) -> str:
        return "Padrão"


@dataclass(frozen=True)
class TaxaSenior(TaxaAdocaoStrategy):
    valor_base: float = 100.0
    desconto_percentual: float = 0.5  # 50%
    senior_a_partir_meses: int = 96   # 8 anos

    def calcular(self, animal: Animal) -> float:
        if animal.idade_meses >= self.senior_a_partir_meses:
            return float(self.valor_base) * (1.0 - self.desconto_percentual)
        return float(self.valor_base)

    def nome(self) -> str:
        return "Sênior (desconto)"


@dataclass(frozen=True)
class TaxaFilhote(TaxaAdocaoStrategy):
    valor_base: float = 100.0
    acrescimo_vacinas: float = 50.0
    filhote_ate_meses: int = 12

    def calcular(self, animal: Animal) -> float:
        if animal.idade_meses <= self.filhote_ate_meses:
            return float(self.valor_base) + float(self.acrescimo_vacinas)
        return float(self.valor_base)

    def nome(self) -> str:
        return "Filhote (vacinas)"


@dataclass(frozen=True)
class TaxaEspecial(TaxaAdocaoStrategy):
    valor_base: float = 100.0
    acrescimo_tratamento: float = 80.0

    def calcular(self, animal: Animal) -> float:
        return float(self.valor_base) + float(self.acrescimo_tratamento)

    def nome(self) -> str:
        return "Especial (tratamento)"
