from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from models.animal_status import AnimalStatus
from models.cachorro import Cachorro
from models.gato import Gato
from models.animal import Animal

"""Camada de persistência (Repository) para animais."""

class AnimalNaoEncontradoError(LookupError):
    """Lançado quando um animal não é encontrado pelo id no repositório."""
    pass

#evita id repetido
class AnimalDuplicadoError(ValueError):
    """Lançado quando tenta cadastrar um animal com id já existente."""
    pass

def animal_from_dict(data: Dict) -> Animal:
    """Reconstrói um objeto Animal (Cachorro/Gato)"""
    status = AnimalStatus(data["status"])
    reservado_por = data.get("reservado_por")
    reserva_ate = data.get("reserva_ate")
    
    #Se vier RESERVADO no JSON, mas faltar dados da reserva, corrige para DISPONIVEL
    if status == AnimalStatus.RESERVADO and (not reservado_por or not reserva_ate):
        status = AnimalStatus.DISPONIVEL

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
            reservado_por=reservado_por,
            reserva_ate=reserva_ate,
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
            reservado_por=reservado_por,
            reserva_ate=reserva_ate,
        )

    raise ValueError(f"Espécie desconhecida no JSON: {especie!r}")


class AnimalRepository:
    """
    Repositório de animais.

    - Mantém os animais em memória (dict).
    - Implementa CRUD: add/get/update/delete/list.
    - Faz persistência em JSON com load/save.
    """
    def __init__(self, arquivo_json: str = "data/animais.json") -> None:
        self._path = Path(arquivo_json)
        self._animais: Dict[str, Animal] = {}

    # CRUD
    """cadastra um novo animal no repositório (memória)."""
    def add(self, animal: Animal) -> None:
        if animal.id in self._animais:
            raise AnimalDuplicadoError(f"Já existe animal com id {animal.id}")
        self._animais[animal.id] = animal
    
    """busca um animal pelo id. Lança erro se não existir."""
    def get(self, animal_id: str) -> Animal:
        if animal_id not in self._animais:
            raise AnimalNaoEncontradoError(f"Animal não encontrado: {animal_id}")
        return self._animais[animal_id]
    
    """atualiza os dados de um animal já existente pelo id."""
    def update(self, animal: Animal) -> None:
        if animal.id not in self._animais:
            raise AnimalNaoEncontradoError(f"Animal não encontrado: {animal.id}")
        self._animais[animal.id] = animal

    """remove um animal pelo id."""
    def delete(self, animal_id: str) -> None:
        if animal_id not in self._animais:
            raise AnimalNaoEncontradoError(f"Animal não encontrado: {animal_id}")
        del self._animais[animal_id]
    
    """Lista animais, com filtros opcionais por status e espécie. Retorna ordenado por data_entrada usando o __lt__ definido em Animal."""
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

    # Persistência
    """Carrega animais do arquivo JSON para a memória do repositório."""
    def load(self) -> None:
        if not self._path.exists():
            return

        raw = json.loads(self._path.read_text(encoding="utf-8"))
        self._animais.clear()
        for item in raw:
            animal = animal_from_dict(item)
            self._animais[animal.id] = animal
    
    """Salva o estado atual do repositório em JSON."""
    def save(self) -> None: #Salva o estado atual em JSON.

        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = [a.to_dict() for a in self._animais.values()]
        self._path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
