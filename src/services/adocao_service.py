from __future__ import annotations

from datetime import datetime, timezone

from infrastructure.animal_repository import AnimalRepository
from models.animal_status import AnimalStatus
from services.taxa_adocao import TaxaAdocaoStrategy, TaxaPadrao


class AdocaoService:
    def __init__(self, repo: AnimalRepository) -> None:
        self.repo = repo

    def adotar(
        self,
        animal_id: str,
        adotante_nome: str,
        strategy: TaxaAdocaoStrategy | None = None,
        termos: str | None = None,
    ) -> str:
        animal = self.repo.get(animal_id)

        #regra: só adota se estiver RESERVADO
        if animal.status != AnimalStatus.RESERVADO:
            raise ValueError("Só é possível adotar animal com status RESERVADO.")

        #regra: o adotante precisa ser quem reservou (se quiser relaxar isso, me diga)
        if animal.reservado_por and animal.reservado_por != adotante_nome:
            raise ValueError("Este animal está reservado por outra pessoa.")

        #regra: se reserva já venceu, não deixa adotar
        if animal.reserva_ate:
            ate = datetime.fromisoformat(animal.reserva_ate)
            if ate.tzinfo is None:
                ate = ate.replace(tzinfo=timezone.utc)
            if ate <= datetime.now(timezone.utc):
                raise ValueError("Reserva expirada. Faça uma nova reserva.")

        strategy = strategy or TaxaPadrao()
        taxa = strategy.calcular(animal)

        #muda status
        animal.mudar_status(AnimalStatus.ADOTADO, motivo=f"Adotado por {adotante_nome}")

        #limpa dados de reserva
        animal.reservado_por = None
        animal.reserva_ate = None

        #registra evento
        animal.registrar_evento("ADOCAO", f"Adoção concluída por {adotante_nome} | taxa={taxa:.2f}")

        #persiste
        self.repo.update(animal)
        self.repo.save()

        #gera contrato (texto simples)
        agora = datetime.now(timezone.utc).isoformat()
        termos_final = termos or "O adotante se compromete a zelar pelo bem-estar do animal."

        contrato = (
            "CONTRATO DE ADOÇÃO\n"
            f"Data: {agora}\n\n"
            f"Adotante: {adotante_nome}\n"
            f"Animal: {animal.nome} | Espécie: {animal.especie} | Raça: {animal.raca} | "
            f"Sexo: {animal.sexo} | Idade (meses): {animal.idade_meses} | Porte: {animal.porte}\n"
            f"Taxa: R$ {taxa:.2f} (estratégia: {strategy.nome()})\n\n"
            "Termos:\n"
            f"- {termos_final}\n"
        )

        return contrato
