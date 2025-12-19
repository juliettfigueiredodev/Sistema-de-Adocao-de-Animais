from __future__ import annotations

from typing import Any, Dict, List, Optional

from models.animal import Animal, ValorInvalidoError
from models.animal_status import AnimalStatus


class Gato(Animal):
    """
    Gato é um Animal com atributo específico:
    - independencia (0 a 10)
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
    ) -> None:
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
        )
        self.independencia = independencia

    @property
    def especie_padrao(self) -> str:
        return "Gato"

    @property
    def independencia(self) -> int:
        return self._independencia

    @independencia.setter
    def independencia(self, value: int) -> None:
        if not isinstance(value, int):
            raise ValorInvalidoError("independencia deve ser um inteiro (0 a 10).")
        if value < 0 or value > 10:
            raise ValorInvalidoError("independencia deve estar entre 0 e 10.")
        self._independencia = value

    def __str__(self) -> str:
        return f"{super().__str__()} | Independência: {self.independencia}/10"

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["independencia"] = self.independencia
        return data
