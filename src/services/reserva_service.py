"""
Serviço responsável pelo gerenciamento de reservas de animais.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from src.infrastructure.animal_repository import AnimalRepository
from src.models.animal import Animal
from src.models.animal_status import AnimalStatus


class ReservaService:
    """
    Gerencia o processo de reserva de animais.
    
    Permite que adotantes reservem animais disponíveis por um
    período determinado (padrão: 48 horas).
    
    Attributes:
        repo: Repositório de animais.
        duracao_horas: Duração da reserva em horas.
    
    Example:
        >>> repo = AnimalRepository()
        >>> service = ReservaService(repo, duracao_horas=48)
        >>> service.reservar("animal-123", "João Silva")
    """
    
    def __init__(
        self, 
        repo: AnimalRepository, 
        duracao_horas: int = 48
    ) -> None:
        """
        Inicializa o serviço de reservas.
        
        Args:
            repo: Repositório para persistência de animais.
            duracao_horas: Duração da reserva em horas (padrão: 48h).
        
        Raises:
            ValueError: Se duracao_horas for menor ou igual a zero.
        """
        if duracao_horas <= 0:
            raise ValueError(
                f"Duração da reserva deve ser positiva: {duracao_horas}"
            )
        
        self.repo = repo
        self.duracao_horas = duracao_horas

    def reservar(self, animal_id: str, adotante_nome: str) -> None:
        """
        Reserva um animal para um adotante.
        
        Valida se o animal está disponível, verifica se há reserva
        expirada e, caso positivo, libera automaticamente antes de
        criar a nova reserva.
        
        Args:
            animal_id: ID único do animal a ser reservado.
            adotante_nome: Nome completo do adotante.
        
        Raises:
            ValueError: Se animal não existir, nome do adotante for vazio,
                       ou animal não estiver disponível.
        
        Example:
            >>> service = ReservaService(repo)
            >>> service.reservar("abc-123", "Maria Santos")
            >>> # Animal agora está RESERVADO por 48h
        """
        # Validação: nome do adotante
        adotante_nome = (adotante_nome or "").strip()
        if not adotante_nome:
            raise ValueError("Nome do adotante é obrigatório para reservar.")

        # Busca animal
        animal = self.repo.get(animal_id)
        if not animal:
            raise ValueError(f"Animal com ID {animal_id} não encontrado")

        # Se estiver RESERVADO, verifica se a reserva já expirou
        if animal.status == AnimalStatus.RESERVADO:
            self._liberar_se_expirado(animal)

        # Validação: só pode reservar se estiver DISPONIVEL
        if animal.status != AnimalStatus.DISPONIVEL:
            raise ValueError(
                f"Só é possível reservar animal com status DISPONIVEL. "
                f"Status atual: {animal.status.value}"
            )

        # Calcula data limite da reserva
        ate = datetime.now(timezone.utc) + timedelta(hours=self.duracao_horas)

        # Atualiza status e campos de reserva
        animal.mudar_status(
            AnimalStatus.RESERVADO, 
            motivo=f"Reservado por {adotante_nome}"
        )
        animal.reservado_por = adotante_nome
        animal.reserva_ate = ate.isoformat()

        # Registra evento no histórico
        animal.registrar_evento(
            "RESERVA", 
            f"Reservado por {adotante_nome} até {animal.reserva_ate}"
        )

        # Persiste mudanças
        self.repo.update(animal)
        self.repo.save()

        print(
            f"[RESERVA] Animal {animal.nome} reservado por {adotante_nome} "
            f"até {animal.reserva_ate}"
        )

    def _liberar_se_expirado(self, animal: Animal) -> None:
        """
        Libera o animal se a reserva já expirou.
        
        Args:
            animal: Animal com reserva a ser verificada.
        """
        if not animal.reserva_ate:
            # Reservado sem data - libera por segurança
            animal.mudar_status(
                AnimalStatus.DISPONIVEL, 
                motivo="Reserva sem data limite (liberado automaticamente)"
            )
            animal.reservado_por = None
            animal.reserva_ate = None
            animal.registrar_evento(
                "RESERVA_EXPIRADA", 
                "Reserva sem data limite foi liberada"
            )
            self.repo.update(animal)
            self.repo.save()
            return

        # Converte data de reserva
        try:
            ate_reserva = datetime.fromisoformat(animal.reserva_ate)
            if ate_reserva.tzinfo is None:
                ate_reserva = ate_reserva.replace(tzinfo=timezone.utc)
        except ValueError:
            # Data inválida - libera por segurança
            animal.mudar_status(
                AnimalStatus.DISPONIVEL, 
                motivo="Reserva com data inválida (liberado automaticamente)"
            )
            animal.reservado_por = None
            animal.reserva_ate = None
            animal.registrar_evento(
                "RESERVA_EXPIRADA", 
                "Reserva com data inválida foi liberada"
            )
            self.repo.update(animal)
            self.repo.save()
            return

        # Verifica se já expirou
        agora = datetime.now(timezone.utc)
        if ate_reserva <= agora:
            animal.mudar_status(
                AnimalStatus.DISPONIVEL, 
                motivo="Reserva expirada (liberado automaticamente ao reservar)"
            )
            animal.reservado_por = None
            animal.reserva_ate = None
            animal.registrar_evento(
                "RESERVA_EXPIRADA", 
                "Reserva expirada foi liberada automaticamente"
            )
            self.repo.update(animal)
            self.repo.save()
            print(
                f"[RESERVA] Reserva expirada de {animal.nome} foi "
                f"liberada automaticamente"
            )

    def __repr__(self) -> str:
        """Representação técnica do serviço."""
        return (
            f"ReservaService(repo={self.repo!r}, "
            f"duracao_horas={self.duracao_horas})"
        )