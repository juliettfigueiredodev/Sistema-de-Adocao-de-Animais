from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from models.animal_status import AnimalStatus
from models.cachorro import Cachorro
from models.gato import Gato
from models.animal import Animal

class AnimalNaoEncontradoError(LookupError):
    pass


class AnimalDuplicadoError(ValueError):
    pass


def animal_from_dict(data: Dict) -> Animal:
    """
    Reconstrói um Animal (Cachorro/Gato) a partir do dict salvo no JSON.

    Por que existe?
    - Porque JSON não sabe “reviver” classes automaticamente.
    - Então precisamos mapear especie -> classe.
    """
    status = AnimalStatus(data["status"])

    especie = data.get("especie")
    if especie == "Cachorro":
        return Cachorro(
            raca=data["raca"],
            nome=data["nome"],
            sexo=data["sexo"],
            idade_meses=int(data["idade_meses"]),
            porte=data["porte"],
            necessidade_passeio=int(data.get("necessidade_passeio", 0)),
            temperamento=data.get("temperamento", []),
            status=status,
            animal_id=data["id"],
            data_entrada=data.get("data_entrada"),
        )

    if especie == "Gato":
        return Gato(
            raca=data["raca"],
            nome=data["nome"],
            sexo=data["sexo"],
            idade_meses=int(data["idade_meses"]),
            porte=data["porte"],
            independencia=int(data.get("independencia", 0)),
            temperamento=data.get("temperamento", []),
            status=status,
            animal_id=data["id"],
            data_entrada=data.get("data_entrada"),
        )

    raise ValueError(f"Espécie desconhecida no JSON: {especie!r}")


class AnimalRepository:
    """
    Repositório = “lugar único” para CRUD.
    Por que isso é bom?
    - Mantém regras de armazenamento separadas do domínio.
    - Depois, se quiser trocar JSON por SQLite, muda aqui e o resto continua igual.
    """

    def __init__(self, arquivo_json: str = "data/animais.json") -> None:
        self._path = Path(arquivo_json)
        self._animais: Dict[str, Animal] = {}

    # ---------- CRUD ----------
    def add(self, animal: Animal) -> None:
        if animal.id in self._animais:
            raise AnimalDuplicadoError(f"Já existe animal com id {animal.id}")
        self._animais[animal.id] = animal

    def get(self, animal_id: str) -> Animal:
        if animal_id not in self._animais:
            raise AnimalNaoEncontradoError(f"Animal não encontrado: {animal_id}")
        return self._animais[animal_id]

    def update(self, animal: Animal) -> None:
        if animal.id not in self._animais:
            raise AnimalNaoEncontradoError(f"Animal não encontrado: {animal.id}")
        self._animais[animal.id] = animal

    def delete(self, animal_id: str) -> None:
        if animal_id not in self._animais:
            raise AnimalNaoEncontradoError(f"Animal não encontrado: {animal_id}")
        del self._animais[animal_id]

    def list(
        self,
        status: Optional[AnimalStatus] = None,
        especie: Optional[str] = None,
    ) -> List[Animal]:
        animais = list(self._animais.values())
        if status is not None:
            animais = [a for a in animais if a.status == status]
        if especie is not None:
            animais = [a for a in animais if a.especie == especie]
        return sorted(animais)  # usa __lt__ (por data_entrada)

    # ---------- Persistência ----------
    def load(self) -> None:
        """
        Carrega do JSON para memória.
        Se não existir arquivo, só começa vazio (sem erro).
        """
        if not self._path.exists():
            return

        raw = json.loads(self._path.read_text(encoding="utf-8"))
        self._animais.clear()
        for item in raw:
            animal = animal_from_dict(item)
            self._animais[animal.id] = animal

    def save(self) -> None:
        """
        Salva o estado atual em JSON.
        """
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = [a.to_dict() for a in self._animais.values()]
        self._path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
