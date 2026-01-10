from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from infrastructure.animal_repository import AnimalRepository
from models.animal_status import AnimalStatus
from services.taxa_adocao import TaxaAdocaoStrategy, TaxaPadrao


class AdocaoService:
    def __init__(self, repo: AnimalRepository, pasta_contratos: str = "data/contratos") -> None:
        self.repo = repo
        self._pasta_contratos = Path(pasta_contratos)

    def adotar(
        self,
        animal_id: str,
        adotante_nome: str,
        strategy: TaxaAdocaoStrategy | None = None,
        termos: str | None = None,
    ) -> str:
        animal = self.repo.get(animal_id)

        # Regra: só adota se estiver RESERVADO
        if animal.status != AnimalStatus.RESERVADO:
            raise ValueError("Só é possível adotar animal com status RESERVADO.")

        # Regra: o adotante precisa ser quem reservou (se tiver reservado_por preenchido)
        if animal.reservado_por and animal.reservado_por != adotante_nome:
            raise ValueError("Este animal está reservado por outra pessoa.")

        # Regra: se reserva já venceu, não deixa adotar
        if animal.reserva_ate:
            try:
                ate = datetime.fromisoformat(animal.reserva_ate)
                if ate.tzinfo is None:
                    ate = ate.replace(tzinfo=timezone.utc)
            except ValueError:
                raise ValueError("Data de reserva inválida. Faça uma nova reserva.")

            if ate <= datetime.now(timezone.utc):
                raise ValueError("Reserva expirada. Faça uma nova reserva.")

        strategy = strategy or TaxaPadrao()
        taxa = strategy.calcular(animal)

        # Muda status
        animal.mudar_status(AnimalStatus.ADOTADO, motivo=f"Adotado por {adotante_nome}")

        # Limpa dados de reserva
        animal.reservado_por = None
        animal.reserva_ate = None

        # Registra evento
        animal.registrar_evento("ADOCAO", f"Adoção concluída por {adotante_nome} | taxa={taxa:.2f}")

        # Persiste
        self.repo.update(animal)
        self.repo.save()

        # Gera contrato (texto simples)
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

        # Salva contrato em arquivo
        self._salvar_contrato_em_arquivo(
            contrato=contrato,
            animal_nome=animal.nome,
            adotante_nome=adotante_nome,
            data_iso=agora,
        )

        return contrato

    def _salvar_contrato_em_arquivo(
        self,
        contrato: str,
        animal_nome: str,
        adotante_nome: str,
        data_iso: str,
    ) -> Path:
        # Cria pasta se não existir
        self._pasta_contratos.mkdir(parents=True, exist_ok=True)

        # Nome de arquivo simples e seguro
        animal_safe = "".join(c for c in animal_nome if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")
        adotante_safe = "".join(c for c in adotante_nome if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")
        data_safe = data_iso.replace(":", "-")

        arquivo = self._pasta_contratos / f"contrato_{animal_safe}_{adotante_safe}_{data_safe}.txt"
        arquivo.write_text(contrato, encoding="utf-8")
        return arquivo
