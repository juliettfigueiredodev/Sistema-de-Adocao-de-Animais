from __future__ import annotations

from enum import Enum
from typing import Dict, FrozenSet


class TransicaoDeEstadoInvalidaError(ValueError):
    """Erro levantado quando tentamos mudar o status do animal por um caminho proibido."""
    pass


class AnimalStatus(str, Enum):
    """Estados possíveis do animal (usado no domínio inteiro)."""

    DISPONIVEL = "DISPONIVEL"
    RESERVADO = "RESERVADO"
    ADOTADO = "ADOTADO"
    DEVOLVIDO = "DEVOLVIDO"
    QUARENTENA = "QUARENTENA"
    INADOTAVEL = "INADOTAVEL"


# Regras essenciais (PDF): transições permitidas
TRANSICOES_PERMITIDAS: Dict[AnimalStatus, FrozenSet[AnimalStatus]] = {
    AnimalStatus.DISPONIVEL: frozenset({AnimalStatus.RESERVADO, AnimalStatus.INADOTAVEL}),
    AnimalStatus.RESERVADO: frozenset({AnimalStatus.ADOTADO}),
    AnimalStatus.ADOTADO: frozenset({AnimalStatus.DEVOLVIDO}),
    AnimalStatus.DEVOLVIDO: frozenset({AnimalStatus.QUARENTENA, AnimalStatus.DISPONIVEL, AnimalStatus.INADOTAVEL}),
    AnimalStatus.QUARENTENA: frozenset({AnimalStatus.DISPONIVEL, AnimalStatus.INADOTAVEL}),
    AnimalStatus.INADOTAVEL: frozenset(),  # estado terminal
}


def validar_transicao(atual: AnimalStatus, novo: AnimalStatus) -> None:
    """Valida se a mudança de status é permitida pelas regras do domínio."""
    permitidos = TRANSICOES_PERMITIDAS.get(atual, frozenset())
    if novo not in permitidos:
        raise TransicaoDeEstadoInvalidaError(
            f"Transição inválida: {atual.value} -> {novo.value}. Permitidos: {[s.value for s in permitidos]}"
        )
