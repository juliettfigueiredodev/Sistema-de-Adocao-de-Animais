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
        
        # valida nome do adotante
        adotante_nome = (adotante_nome or "").strip()
        if not adotante_nome:
            raise ValueError("Nome do adotante é obrigatório para reservar.")

        # se estiver RESERVADO, mas a reserva já venceu, libera automaticamente
        if animal.status == AnimalStatus.RESERVADO and animal.reserva_ate:
            try:
                ate_reserva = datetime.fromisoformat(animal.reserva_ate)
                if ate_reserva.tzinfo is None:
                    ate_reserva = ate_reserva.replace(tzinfo=timezone.utc)
            except ValueError:
                ate_reserva = None

            agora = datetime.now(timezone.utc)
            if ate_reserva and ate_reserva <= agora:
                animal.mudar_status(AnimalStatus.DISPONIVEL, motivo="Reserva expirada (auto)")
                animal.reservado_por = None
                animal.reserva_ate = None
                animal.registrar_evento("RESERVA_EXPIRADA", "Reserva expirada automaticamente (ao reservar)")
                self.repo.update(animal)
                self.repo.save()

        #Regra: só pode reservar se estiver DISPONIVEL
        if animal.status != AnimalStatus.DISPONIVEL:
            raise ValueError("Só é possível reservar animal com status DISPONIVEL (sem reserva ativa).")


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
