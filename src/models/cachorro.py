"""
Módulo contendo a classe Cachorro.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.models.animal import Animal, ValorInvalidoError
from src.models.animal_status import AnimalStatus


class Cachorro(Animal):
    """
    Representa um cachorro no sistema de adoção.
    
    Estende a classe Animal adicionando atributos específicos
    de cachorros, como necessidade de passeio.
    
    Attributes:
        necessidade_passeio: Nível de necessidade de passeio (0-10).
            0 = Cachorro muito sedentário
            10 = Cachorro muito ativo que precisa de muito exercício
    
    Example:
        >>> cachorro = Cachorro(
        ...     raca="Labrador",
        ...     nome="Rex",
        ...     sexo="M",
        ...     idade_meses=24,
        ...     porte="G",
        ...     necessidade_passeio=8,
        ...     temperamento=["docil", "energico"]
        ... )
        >>> print(cachorro)
        [uuid] Rex (Cachorro/Labrador) - ... | Passeio: 8/10
    """

    def __init__(
        self,
        raca: str,
        nome: str,
        sexo: str,
        idade_meses: int,
        porte: str,
        necessidade_passeio: int,
        temperamento: Optional[List[str]] = None,
        status: AnimalStatus = AnimalStatus.DISPONIVEL,
        animal_id: Optional[str] = None,
        data_entrada: Optional[str] = None,
        reservado_por: Optional[str] = None,
        reserva_ate: Optional[str] = None,
    ) -> None:
        """
        Inicializa um novo cachorro.
        
        Args:
            raca: Raça do cachorro.
            nome: Nome do cachorro.
            sexo: Sexo do cachorro.
            idade_meses: Idade em meses.
            porte: Porte físico (P/M/G).
            necessidade_passeio: Nível de necessidade de passeio (0-10).
            temperamento: Lista de características comportamentais.
            status: Status inicial (padrão: DISPONIVEL).
            animal_id: ID único (gerado automaticamente se None).
            data_entrada: Data de entrada (gerada automaticamente se None).
            reservado_por: ID do adotante que reservou (se houver).
            reserva_ate: Data limite da reserva (se houver).
        
        Raises:
            ValorInvalidoError: Se necessidade_passeio não estiver entre 0 e 10.
        """
        self._necessidade_passeio = 0
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
        self.necessidade_passeio = necessidade_passeio

    @property
    def especie_padrao(self) -> str:
        """Retorna a espécie padrão: Cachorro."""
        return "Cachorro"

    @property
    def necessidade_passeio(self) -> int:
        """Nível de necessidade de passeio (0-10)."""
        return self._necessidade_passeio

    @necessidade_passeio.setter
    def necessidade_passeio(self, value: int) -> None:
        """
        Define a necessidade de passeio com validação.
        
        Args:
            value: Nível de necessidade (0-10).
        
        Raises:
            ValorInvalidoError: Se não for inteiro ou estiver fora do range.
        """
        if not isinstance(value, int):
            raise ValorInvalidoError("necessidade_passeio deve ser um inteiro (0 a 10).")
        if value < 0 or value > 10:
            raise ValorInvalidoError("necessidade_passeio deve estar entre 0 e 10.")
        self._necessidade_passeio = value

    def __str__(self) -> str:
        """Representação amigável do cachorro."""
        return f"{super().__str__()} | Passeio: {self.necessidade_passeio}/10"

    def __repr__(self) -> str:
        """Representação técnica do cachorro."""
        return (
            f"Cachorro(id={self.id!r}, nome={self.nome!r}, raca={self.raca!r}, "
            f"porte={self.porte!r}, necessidade_passeio={self.necessidade_passeio})"
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializa o cachorro para dicionário.
        
        Returns:
            Dicionário com todos os atributos, incluindo necessidade_passeio.
        """
        data = super().to_dict()
        data["necessidade_passeio"] = self.necessidade_passeio
        return data