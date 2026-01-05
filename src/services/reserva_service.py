from __future__ import annotations

from datetime import datetime, timedelta, timezone

from models.animal_status import AnimalStatus
from infrastructure.animal_repository import AnimalRepository


class ReservaService:
    def __init__(self, repo: AnimalRepository, duracao_horas: int = 48) -> None:
        self.repo = repo
        self.duracao_horas = duracao_horas

    def reservar(self, animal_id: str, adotante_nome: str) -> None:
        animal = self.repo.get(animal_id)

        #Regra: só pode reservar se estiver DISPONIVEL
        if animal.status != AnimalStatus.DISPONIVEL:
            raise ValueError("Só é possível reservar animal com status DISPONIVEL.")

        #janela de reserva (agora + 48h)
        ate = datetime.now(timezone.utc) + timedelta(hours=self.duracao_horas)

        #Atualiza status e campos de reserva
        animal.mudar_status(AnimalStatus.RESERVADO, motivo=f"Reservado por {adotante_nome}")
        animal.reservado_por = adotante_nome
        animal.reserva_ate = ate.isoformat()

        #Registra evento no histórico
        animal.registrar_evento("RESERVA", f"Reservado por {adotante_nome} até {animal.reserva_ate}")

        #Persiste
        self.repo.update(animal)
        self.repo.save()
