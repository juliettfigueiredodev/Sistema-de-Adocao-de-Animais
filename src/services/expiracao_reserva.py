from __future__ import annotations

from datetime import datetime, timezone

from models.animal_status import AnimalStatus
from infrastructure.animal_repository import AnimalRepository


class ExpiracaoReservaJob:
    def __init__(self, repo: AnimalRepository) -> None:
        self.repo = repo

    def executar(self) -> int:
        agora = datetime.now(timezone.utc)
        expirados = 0

        for animal in self.repo.list():
            if animal.status != AnimalStatus.RESERVADO:
                continue

            if not animal.reserva_ate:
                continue

            try:
                ate = datetime.fromisoformat(animal.reserva_ate)
                if ate.tzinfo is None:
                    ate = ate.replace(tzinfo=timezone.utc)
            except ValueError:
                # se a data estiver em formato inválido, ignora
                continue

            if ate <= agora:
                print(f"[JOB] Expirando reserva: id={animal.id} nome={animal.nome} status={animal.status.value} reserva_ate={animal.reserva_ate}")

                animal.mudar_status(AnimalStatus.DISPONIVEL, motivo="Reserva expirada")
                animal.reservado_por = None
                animal.reserva_ate = None
                animal.registrar_evento("RESERVA_EXPIRADA", "Reserva expirada automaticamente")

                self.repo.update(animal)
                expirados += 1

        if expirados > 0:
            self.repo.save()

        return expirados
