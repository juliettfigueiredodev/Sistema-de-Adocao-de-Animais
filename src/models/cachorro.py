from __future__ import annotations

from typing import Any, Dict, List, Optional

from .animal import Animal, ValorInvalidoError
from .animal_status import AnimalStatus


class Cachorro(Animal):
    """
    Cachorro é um Animal com atributo específico:
    - necessidade_passeio (0 a 10)
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
    ) -> None:
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
        )
        self.necessidade_passeio = necessidade_passeio

    @property
    def especie_padrao(self) -> str:
        return "Cachorro"

    @property
    def necessidade_passeio(self) -> int:
        return self._necessidade_passeio

    @necessidade_passeio.setter
    def necessidade_passeio(self, value: int) -> None:
        if not isinstance(value, int):
            raise ValorInvalidoError("necessidade_passeio deve ser um inteiro (0 a 10).")
        if value < 0 or value > 10:
            raise ValorInvalidoError("necessidade_passeio deve estar entre 0 e 10.")
        self._necessidade_passeio = value

    def __str__(self) -> str:
        return f"{super().__str__()} | Passeio: {self.necessidade_passeio}/10"

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["necessidade_passeio"] = self.necessidade_passeio
        return data
