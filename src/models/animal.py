"""
Módulo base para representação de animais no sistema de adoção.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterator, List, Optional
from uuid import uuid4

from src.models.animal_status import AnimalStatus, validar_transicao


class ValorInvalidoError(ValueError):
    """
    Exceção lançada quando um valor de atributo do animal é inválido.
    
    Exemplos: porte inválido, idade negativa, temperamento mal formatado.
    """
    pass


@dataclass(frozen=True)
class AnimalEvent:
    """
    Evento imutável no histórico do animal.
    
    Attributes:
        tipo: Tipo do evento (ENTRADA, MUDANCA_STATUS, VACINA, etc).
        detalhes: Descrição detalhada do evento.
        timestamp: Data/hora em formato ISO8601.
    """
    tipo: str
    detalhes: str
    timestamp: str  # ISO8601

    @staticmethod
    def novo(tipo: str, detalhes: str) -> "AnimalEvent":
        """Cria um novo evento com timestamp atual."""
        ts = datetime.now(timezone.utc).isoformat()
        return AnimalEvent(tipo=tipo, detalhes=detalhes, timestamp=ts)


class Animal(ABC):
    """
    Classe abstrata base para representação de animais.
    
    Define a interface comum para todos os animais do sistema,
    incluindo atributos obrigatórios, validações, histórico de eventos
    e regras de transição de status.
    
    Attributes:
        id: Identificador único do animal (UUID).
        data_entrada: Data/hora de entrada no sistema (ISO8601).
        especie: Espécie do animal (Cachorro, Gato, etc).
        raca: Raça do animal.
        nome: Nome do animal.
        sexo: Sexo do animal.
        idade_meses: Idade em meses.
        porte: Porte físico (P, M ou G).
        temperamento: Lista de características comportamentais.
        status: Status atual (DISPONIVEL, RESERVADO, etc).
    """
    
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
        reservado_por: Optional[str] = None,
        reserva_ate: Optional[str] = None,
    ) -> None:
        self._id = animal_id or str(uuid4())
        self._data_entrada = data_entrada or datetime.now(timezone.utc).isoformat()
        self._reservado_por = reservado_por
        self._reserva_ate = reserva_ate

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
        """Retorna a espécie padrão da classe concreta (Cachorro, Gato, etc)."""
        raise NotImplementedError

    # Propriedades
    
    @property
    def id(self) -> str:
        """Identificador único do animal."""
        return self._id

    @property
    def data_entrada(self) -> str:
        """Data/hora de entrada no sistema (ISO8601)."""
        return self._data_entrada
 
    @property
    def reservado_por(self) -> Optional[str]:
        """ID do adotante que reservou o animal (se houver)."""
        return self._reservado_por

    @reservado_por.setter
    def reservado_por(self, value: Optional[str]) -> None:
        self._reservado_por = value

    @property
    def reserva_ate(self) -> Optional[str]:
        """Data/hora limite da reserva (ISO8601)."""
        return self._reserva_ate

    @reserva_ate.setter
    def reserva_ate(self, value: Optional[str]) -> None:
        self._reserva_ate = value

    @property
    def especie(self) -> str:
        """Espécie do animal."""
        return self._especie

    @especie.setter
    def especie(self, value: str) -> None:
        value = (value or "").strip()
        if not value:
            raise ValorInvalidoError("Espécie é obrigatória.")
        self._especie = value

    @property
    def raca(self) -> str:
        """Raça do animal."""
        return self._raca

    @raca.setter
    def raca(self, value: str) -> None:
        value = (value or "").strip()
        if not value:
            raise ValorInvalidoError("Raça é obrigatória.")
        self._raca = value

    @property
    def nome(self) -> str:
        """Nome do animal."""
        return self._nome

    @nome.setter
    def nome(self, value: str) -> None:
        value = (value or "").strip()
        if not value:
            raise ValorInvalidoError("Nome é obrigatório.")
        self._nome = value

    @property
    def sexo(self) -> str:
        """Sexo do animal."""
        return self._sexo

    @sexo.setter
    def sexo(self, value: str) -> None:
        value = (value or "").strip()
        if not value:
            raise ValorInvalidoError("Sexo é obrigatório.")
        self._sexo = value

    @property
    def idade_meses(self) -> int:
        """Idade do animal em meses."""
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
        """Porte físico do animal (P, M ou G)."""
        return self._porte

    @porte.setter
    def porte(self, value: str) -> None:
        value = (value or "").strip().upper()
        if value not in self.PORTES_VALIDOS:
            raise ValorInvalidoError("Porte inválido. Use 'P', 'M' ou 'G'.")
        self._porte = value

    @property
    def temperamento(self) -> List[str]:
        """Lista de características comportamentais do animal."""
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
        """Status atual do animal no sistema."""
        return self._status

    # Regras de domínio
    
    def mudar_status(self, novo_status: AnimalStatus, motivo: str = "") -> None:
        """
        Muda o status do animal validando a transição.
        
        Args:
            novo_status: Novo status desejado.
            motivo: Motivo da mudança (opcional).
        
        Raises:
            TransicaoDeEstadoInvalidaError: Se a transição for inválida.
        """
        validar_transicao(self._status, novo_status)
        anterior = self._status
        self._status = novo_status
        detalhe = f"{anterior.value} -> {novo_status.value}"
        if motivo:
            detalhe += f" | motivo: {motivo}"
        self._registrar_evento("MUDANCA_STATUS", detalhe)

    def registrar_evento(self, tipo: str, detalhes: str) -> None:
        """
        API pública para registrar fatos relevantes.
        
        Args:
            tipo: Tipo do evento (VACINA, TRIAGEM, etc).
            detalhes: Descrição detalhada do evento.
        """
        self._registrar_evento(tipo, detalhes)

    def _registrar_evento(self, tipo: str, detalhes: str) -> None:
        """Método interno para adicionar eventos ao histórico."""
        self._historico.append(AnimalEvent.novo(tipo=tipo, detalhes=detalhes))

    # Persistência (JSON)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializa o animal para dicionário.
        
        Returns:
            Dicionário com todos os atributos do animal.
        """
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
            "reservado_por": self.reservado_por,
            "reserva_ate": self.reserva_ate,
            "historico": [e.__dict__ for e in self._historico],
        }