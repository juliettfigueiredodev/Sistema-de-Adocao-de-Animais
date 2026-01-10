"""
Módulo de estados e transições de status dos animais.

Define os status possíveis de um animal no sistema de adoção
e as regras de transição válidas entre eles.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, FrozenSet


class TransicaoDeEstadoInvalidaError(ValueError):
    """
    Exceção lançada quando há tentativa de transição
    inválida de estado do animal.
    
    Example:
        >>> raise TransicaoDeEstadoInvalidaError(
        ...     "Não é possível ir de ADOTADO para DISPONIVEL"
        ... )
    """
    pass


class AnimalStatus(str, Enum):
    """
    Estados possíveis de um animal no sistema de adoção.
    
    Attributes:
        DISPONIVEL: Animal disponível para reserva/adoção.
        RESERVADO: Animal reservado por um adotante (48h).
        ADOTADO: Animal adotado com sucesso.
        DEVOLVIDO: Animal devolvido pelo adotante.
        QUARENTENA: Animal em quarentena (saúde/comportamento).
        INADOTAVEL: Animal considerado inadotável (estado terminal).
    """

    DISPONIVEL = "DISPONIVEL"
    RESERVADO = "RESERVADO"
    ADOTADO = "ADOTADO"
    DEVOLVIDO = "DEVOLVIDO"
    QUARENTENA = "QUARENTENA"
    INADOTAVEL = "INADOTAVEL"


# Regras essenciais: transições permitidas
TRANSICOES_PERMITIDAS: Dict[AnimalStatus, FrozenSet[AnimalStatus]] = {
    AnimalStatus.DISPONIVEL: frozenset({
        AnimalStatus.RESERVADO, 
        AnimalStatus.INADOTAVEL
    }),
    AnimalStatus.RESERVADO: frozenset({
        AnimalStatus.ADOTADO, 
        AnimalStatus.DISPONIVEL
    }),
    AnimalStatus.ADOTADO: frozenset({
        AnimalStatus.DEVOLVIDO
    }),
    AnimalStatus.DEVOLVIDO: frozenset({
        AnimalStatus.QUARENTENA, 
        AnimalStatus.DISPONIVEL, 
        AnimalStatus.INADOTAVEL
    }),
    AnimalStatus.QUARENTENA: frozenset({
        AnimalStatus.DISPONIVEL, 
        AnimalStatus.INADOTAVEL
    }),
    AnimalStatus.INADOTAVEL: frozenset(),  # estado terminal
}


def validar_transicao(atual: AnimalStatus, novo: AnimalStatus) -> None:
    """
    Valida se a transição de status é permitida.
    
    Args:
        atual: Status atual do animal.
        novo: Novo status desejado.
    
    Raises:
        TransicaoDeEstadoInvalidaError: Se a transição for inválida.
    
    Example:
        >>> validar_transicao(AnimalStatus.DISPONIVEL, AnimalStatus.RESERVADO)
        >>> # OK, transição válida
        >>> 
        >>> validar_transicao(AnimalStatus.ADOTADO, AnimalStatus.DISPONIVEL)
        TransicaoDeEstadoInvalidaError: Transição inválida...
    """
    permitidos = TRANSICOES_PERMITIDAS.get(atual, frozenset())
    if novo not in permitidos:
        raise TransicaoDeEstadoInvalidaError(
            f"Transição inválida: {atual.value} -> {novo.value}. "
            f"Permitidos: {[s.value for s in permitidos]}"
        )