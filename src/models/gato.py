"""
Módulo contendo a classe Gato.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.models.animal import Animal, ValorInvalidoError
from src.models.animal_status import AnimalStatus


class Gato(Animal):
    """
    Representa um gato no sistema de adoção.
    
    Estende a classe Animal adicionando atributos específicos
    de gatos, como nível de independência.
    
    Attributes:
        independencia: Nível de independência do gato (0-10).
            0 = Gato muito dependente, precisa de atenção constante
            10 = Gato muito independente, pode ficar sozinho facilmente
    
    Example:
        >>> gato = Gato(
        ...     raca="Siamês",
        ...     nome="Mimi",
        ...     sexo="F",
        ...     idade_meses=18,
        ...     porte="P",
        ...     independencia=7,
        ...     temperamento=["calmo", "carinhoso"]
        ... )
        >>> print(gato)
        [uuid] Mimi (Gato/Siamês) - ... | Independência: 7/10
    """

    def __init__(
        self,
        raca: str,
        nome: str,
        sexo: str,
        idade_meses: int,
        porte: str,
        independencia: int,
        temperamento: Optional[List[str]] = None,
        status: AnimalStatus = AnimalStatus.DISPONIVEL,
        animal_id: Optional[str] = None,
        data_entrada: Optional[str] = None,
        reservado_por: Optional[str] = None,
        reserva_ate: Optional[str] = None,
    ) -> None:
        """
        Inicializa um novo gato.
        
        Args:
            raca: Raça do gato.
            nome: Nome do gato.
            sexo: Sexo do gato.
            idade_meses: Idade em meses.
            porte: Porte físico (P/M/G).
            independencia: Nível de independência (0-10).
            temperamento: Lista de características comportamentais.
            status: Status inicial (padrão: DISPONIVEL).
            animal_id: ID único (gerado automaticamente se None).
            data_entrada: Data de entrada (gerada automaticamente se None).
            reservado_por: ID do adotante que reservou (se houver).
            reserva_ate: Data limite da reserva (se houver).
        
        Raises:
            ValorInvalidoError: Se independencia não estiver entre 0 e 10.
        """
        self._independencia = 0
        super().__init__(
            especie=self.especie_padrao,
            raca=raca,
            nome=nome,
            sexo=sexo,
            idade_meses=idade_meses,
            porte=porte,
            temperamento=temperamento,
            status=status,
            animal_id=animal_id,
            data_entrada=data_entrada,
            reservado_por=reservado_por,
            reserva_ate=reserva_ate,
        )
        self.independencia = independencia

    @property
    def especie_padrao(self) -> str:
        """Retorna a espécie padrão: Gato."""
        return "Gato"

    @property
    def independencia(self) -> int:
        """Nível de independência (0-10)."""
        return self._independencia

    @independencia.setter
    def independencia(self, value: int) -> None:
        """
        Define o nível de independência com validação.
        
        Args:
            value: Nível de independência (0-10).
        
        Raises:
            ValorInvalidoError: Se não for inteiro ou estiver fora do range.
        """
        if not isinstance(value, int):
            raise ValorInvalidoError("independencia deve ser um inteiro (0 a 10).")
        if value < 0 or value > 10:
            raise ValorInvalidoError("independencia deve estar entre 0 e 10.")
        self._independencia = value

    def __str__(self) -> str:
        """Representação amigável do gato."""
        return f"{super().__str__()} | Independência: {self.independencia}/10"

    def __repr__(self) -> str:
        """Representação técnica do gato."""
        return (
            f"Gato(id={self.id!r}, nome={self.nome!r}, raca={self.raca!r}, "
            f"porte={self.porte!r}, independencia={self.independencia})"
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializa o gato para dicionário.
        
        Returns:
            Dicionário com todos os atributos, incluindo independencia.
        """
        data = super().to_dict()
        data["independencia"] = self.independencia
        return data