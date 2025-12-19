from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterator, List, Optional
from uuid import uuid4

from models.animal_status import AnimalStatus, validar_transicao


class ValorInvalidoError(ValueError):
    pass


@dataclass(frozen=True)
class AnimalEvent:
    tipo: str
    detalhes: str
    timestamp: str  # ISO8601

    @staticmethod
    def novo(tipo: str, detalhes: str) -> "AnimalEvent":
        ts = datetime.now(timezone.utc).isoformat()
        return AnimalEvent(tipo=tipo, detalhes=detalhes, timestamp=ts)


class Animal(ABC):
    PORTES_VALIDOS = {"P", "M", "G"}

    def __init__(
        self,
        especie: str,
        raca: str,
        nome: str,
        sexo: str,
        idade_meses: int,
        porte: str,
        temperamento: Optional[List[str]] = None,
        status: AnimalStatus = AnimalStatus.DISPONIVEL,
        animal_id: Optional[str] = None,
        data_entrada: Optional[str] = None,
    ) -> None:
        self._id = animal_id or str(uuid4())
        self._data_entrada = data_entrada or datetime.now(timezone.utc).isoformat()

        self._especie = ""
        self._raca = ""
        self._nome = ""
        self._sexo = ""
        self._idade_meses = 0
        self._porte = ""

        self.especie = especie
        self.raca = raca
        self.nome = nome
        self.sexo = sexo
        self.idade_meses = idade_meses
        self.porte = porte

        self._temperamento: List[str] = []
        self.temperamento = temperamento or []

        self._status: AnimalStatus = status

        self._historico: List[AnimalEvent] = []
        self._registrar_evento("ENTRADA", f"Animal cadastrado com status {self._status.value}")

    # Métodos especiais

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(id={self.id!r}, nome={self.nome!r}, "
            f"especie={self.especie!r}, porte={self.porte!r}, status={self.status.value!r})"
        )

    def __str__(self) -> str:
        return (
            f"[{self.id}] {self.nome} ({self.especie}/{self.raca}) - "
            f"Sexo: {self.sexo} | Idade: {self.idade_meses}m | Porte: {self.porte} | Status: {self.status.value}"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Animal):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __lt__(self, other: "Animal") -> bool:
        # Ordena por data de entrada (mais antigo primeiro)
        return self.data_entrada < other.data_entrada

    def __iter__(self) -> Iterator[AnimalEvent]:
        # Permite: for evento in animal
        return iter(self._historico)

    @property
    @abstractmethod
    def especie_padrao(self) -> str:
        raise NotImplementedError

    # Propriedades
    
    @property
    def id(self) -> str:
        return self._id

    @property
    def data_entrada(self) -> str:
        return self._data_entrada

    @property
    def especie(self) -> str:
        return self._especie

    @especie.setter
    def especie(self, value: str) -> None:
        value = (value or "").strip()
        if not value:
            raise ValorInvalidoError("Espécie é obrigatória.")
        self._especie = value

    @property
    def raca(self) -> str:
        return self._raca

    @raca.setter
    def raca(self, value: str) -> None:
        value = (value or "").strip()
        if not value:
            raise ValorInvalidoError("Raça é obrigatória.")
        self._raca = value

    @property
    def nome(self) -> str:
        return self._nome

    @nome.setter
    def nome(self, value: str) -> None:
        value = (value or "").strip()
        if not value:
            raise ValorInvalidoError("Nome é obrigatório.")
        self._nome = value

    @property
    def sexo(self) -> str:
        return self._sexo

    @sexo.setter
    def sexo(self, value: str) -> None:
        value = (value or "").strip()
        if not value:
            raise ValorInvalidoError("Sexo é obrigatório.")
        self._sexo = value

    @property
    def idade_meses(self) -> int:
        return self._idade_meses

    @idade_meses.setter
    def idade_meses(self, value: int) -> None:
        if not isinstance(value, int):
            raise ValorInvalidoError("Idade (em meses) deve ser um inteiro.")
        if value < 0:
            raise ValorInvalidoError("Idade (em meses) não pode ser negativa.")
        self._idade_meses = value

    @property
    def porte(self) -> str:
        return self._porte

    @porte.setter
    def porte(self, value: str) -> None:
        value = (value or "").strip().upper()
        if value not in self.PORTES_VALIDOS:
            raise ValorInvalidoError("Porte inválido. Use 'P', 'M' ou 'G'.")
        self._porte = value

    @property
    def temperamento(self) -> List[str]:
        return list(self._temperamento)

    @temperamento.setter
    def temperamento(self, value: List[str]) -> None:
        if value is None:
            self._temperamento = []
            return
        if not isinstance(value, list):
            raise ValorInvalidoError("Temperamento deve ser uma lista de strings.")
        limpo: List[str] = []
        for item in value:
            if not isinstance(item, str) or not item.strip():
                raise ValorInvalidoError("Temperamento deve conter apenas strings não vazias.")
            limpo.append(item.strip().lower())
        seen = set()
        final: List[str] = []
        for t in limpo:
            if t not in seen:
                seen.add(t)
                final.append(t)
        self._temperamento = final

    @property
    def status(self) -> AnimalStatus:
        return self._status

    # Regras de domínio
    
    def mudar_status(self, novo_status: AnimalStatus, motivo: str = "") -> None:
        validar_transicao(self._status, novo_status)
        anterior = self._status
        self._status = novo_status
        detalhe = f"{anterior.value} -> {novo_status.value}"
        if motivo:
            detalhe += f" | motivo: {motivo}"
        self._registrar_evento("MUDANCA_STATUS", detalhe)

    def registrar_evento(self, tipo: str, detalhes: str) -> None:
        """API pública para registrar fatos relevantes (vacina, triagem, etc.)."""
        self._registrar_evento(tipo, detalhes)

    def _registrar_evento(self, tipo: str, detalhes: str) -> None:
        self._historico.append(AnimalEvent.novo(tipo=tipo, detalhes=detalhes))

    # Persistência (ajuda no JSON depois)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "data_entrada": self.data_entrada,
            "especie": self.especie,
            "raca": self.raca,
            "nome": self.nome,
            "sexo": self.sexo,
            "idade_meses": self.idade_meses,
            "porte": self.porte,
            "temperamento": self.temperamento,
            "status": self.status.value,
            "historico": [e.__dict__ for e in self._historico],
        }
