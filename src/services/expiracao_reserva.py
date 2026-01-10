"""
Serviço de job para expirar reservas vencidas automaticamente.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from src.infrastructure.animal_repository import AnimalRepository
from src.models.animal import Animal
from src.models.animal_status import AnimalStatus


class ExpiracaoReservaJob:
    """
    Job responsável por expirar reservas que ultrapassaram o prazo.
    
    Percorre todos os animais com status RESERVADO e verifica se
    a data limite (reserva_ate) já passou. Se sim, retorna o animal
    para status DISPONIVEL.
    
    Attributes:
        repo: Repositório de animais.
    
    Example:
        >>> repo = AnimalRepository()
        >>> job = ExpiracaoReservaJob(repo)
        >>> expirados = job.executar()
        >>> print(f"{expirados} reservas expiradas")
    """
    
    def __init__(self, repo: AnimalRepository) -> None:
        """
        Inicializa o job de expiração.
        
        Args:
            repo: Repositório para buscar e atualizar animais.
        """
        self.repo = repo

    def executar(self) -> int:
        """
        Executa o processo de expiração de reservas.
        
        Percorre todos os animais reservados e expira aqueles
        cuja data limite já passou.
        
        Returns:
            Número de reservas expiradas.
        
        Example:
            >>> job = ExpiracaoReservaJob(repo)
            >>> total = job.executar()
            >>> print(f"Total de reservas expiradas: {total}")
        """
        agora = datetime.now(timezone.utc)
        expirados = 0
        
        animais_para_expirar: List[Animal] = []

        # Identifica animais com reserva expirada
        for animal in self.repo.list():
            if animal.status != AnimalStatus.RESERVADO:
                continue

            if not animal.reserva_ate:
                # Animal reservado sem data limite - situação anômala
                print(
                    f"[AVISO] Animal {animal.id} ({animal.nome}) está RESERVADO "
                    f"mas sem reserva_ate. Expirando automaticamente."
                )
                animais_para_expirar.append(animal)
                continue

            # Converte data de reserva para datetime
            try:
                ate = datetime.fromisoformat(animal.reserva_ate)
                if ate.tzinfo is None:
                    ate = ate.replace(tzinfo=timezone.utc)
            except ValueError:
                # Data inválida - expira por segurança
                print(
                    f"[ERRO] Animal {animal.id} ({animal.nome}) tem "
                    f"reserva_ate inválida: {animal.reserva_ate}. Expirando."
                )
                animais_para_expirar.append(animal)
                continue

            # Verifica se já passou do prazo
            if ate <= agora:
                print(
                    f"[JOB] Expirando reserva: id={animal.id} nome={animal.nome} "
                    f"reservado_por={animal.reservado_por} "
                    f"reserva_ate={animal.reserva_ate}"
                )
                animais_para_expirar.append(animal)

        # Expira todos os identificados
        for animal in animais_para_expirar:
            self._expirar_reserva(animal)
            expirados += 1

        # Salva mudanças no repositório (batch)
        if expirados > 0:
            self.repo.save()
            print(f"[JOB] Total de reservas expiradas: {expirados}")

        return expirados

    def _expirar_reserva(self, animal: Animal) -> None:
        """
        Expira a reserva de um animal específico.
        
        Args:
            animal: Animal cuja reserva será expirada.
        """
        animal.mudar_status(
            AnimalStatus.DISPONIVEL, 
            motivo="Reserva expirada automaticamente"
        )
        
        # Limpa dados de reserva
        animal.reservado_por = None
        animal.reserva_ate = None
        
        # Registra evento
        animal.registrar_evento(
            "RESERVA_EXPIRADA", 
            "Reserva expirada automaticamente pelo sistema"
        )
        
        # Atualiza no repositório
        self.repo.update(animal)

    def __repr__(self) -> str:
        """Representação técnica do job."""
        return f"ExpiracaoReservaJob(repo={self.repo!r})"