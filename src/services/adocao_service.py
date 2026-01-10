"""
Serviço responsável pelo processo de adoção de animais.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from src.infrastructure.animal_repository import AnimalRepository
from src.models.animal import Animal
from src.models.animal_status import AnimalStatus
from src.services.taxa_adocao import TaxaAdocaoStrategy, TaxaPadrao


class AdocaoService:
    """
    Gerencia o processo de adoção de animais.
    
    Responsável por validar condições de adoção, calcular taxas,
    gerar contratos e atualizar o status dos animais.
    
    Attributes:
        repo: Repositório de animais.
        pasta_contratos: Diretório onde os contratos são salvos.
    
    Example:
        >>> repo = AnimalRepository()
        >>> service = AdocaoService(repo)
        >>> contrato = service.adotar(
        ...     animal_id="abc-123",
        ...     adotante_nome="João Silva"
        ... )
    """
    
    def __init__(
        self, 
        repo: AnimalRepository, 
        pasta_contratos: str = "data/contratos"
    ) -> None:
        """
        Inicializa o serviço de adoção.
        
        Args:
            repo: Repositório para persistência de animais.
            pasta_contratos: Caminho para armazenar contratos gerados.
        """
        self.repo = repo
        self._pasta_contratos = Path(pasta_contratos)

    def adotar(
        self,
        animal_id: str,
        adotante_nome: str,
        strategy: Optional[TaxaAdocaoStrategy] = None,
        termos: Optional[str] = None,
    ) -> str:
        """
        Realiza a adoção de um animal.
        
        Valida se o animal está reservado, se a reserva não expirou,
        calcula a taxa, muda o status para ADOTADO e gera o contrato.
        
        Args:
            animal_id: ID único do animal a ser adotado.
            adotante_nome: Nome completo do adotante.
            strategy: Estratégia de cálculo de taxa (padrão: TaxaPadrao).
            termos: Termos adicionais do contrato (opcional).
        
        Returns:
            String contendo o contrato de adoção formatado.
        
        Raises:
            ValueError: Se animal não existir, não estiver reservado,
                       reserva expirou ou foi reservado por outra pessoa.
        
        Example:
            >>> contrato = service.adotar(
            ...     animal_id="abc-123",
            ...     adotante_nome="Maria Santos",
            ...     strategy=TaxaSenior()
            ... )
        """
        animal = self.repo.get(animal_id)
        if not animal:
            raise ValueError(f"Animal com ID {animal_id} não encontrado")

        # Validação 1: Só adota se estiver RESERVADO
        if animal.status != AnimalStatus.RESERVADO:
            raise ValueError(
                f"Só é possível adotar animal com status RESERVADO. "
                f"Status atual: {animal.status.value}"
            )

        # Validação 2: O adotante precisa ser quem reservou
        if animal.reservado_por and animal.reservado_por != adotante_nome:
            raise ValueError(
                f"Este animal está reservado por {animal.reservado_por}. "
                f"Apenas quem reservou pode adotar."
            )

        # Validação 3: Reserva não pode ter expirado
        if animal.reserva_ate:
            try:
                ate = datetime.fromisoformat(animal.reserva_ate)
                if ate.tzinfo is None:
                    ate = ate.replace(tzinfo=timezone.utc)
            except ValueError:
                raise ValueError(
                    "Data de reserva inválida no sistema. "
                    "Faça uma nova reserva."
                )

            if ate <= datetime.now(timezone.utc):
                raise ValueError(
                    "Reserva expirada. Faça uma nova reserva para este animal."
                )

        # Calcula taxa usando estratégia
        strategy = strategy or TaxaPadrao()
        taxa = strategy.calcular(animal)

        # Muda status para ADOTADO
        animal.mudar_status(
            AnimalStatus.ADOTADO, 
            motivo=f"Adotado por {adotante_nome}"
        )

        # Limpa dados de reserva
        animal.reservado_por = None
        animal.reserva_ate = None

        # Registra evento de adoção
        animal.registrar_evento(
            "ADOCAO", 
            f"Adoção concluída por {adotante_nome} | taxa=R$ {taxa:.2f}"
        )

        # Persiste no repositório
        self.repo.update(animal)
        self.repo.save()

        # Gera e salva contrato
        contrato = self._gerar_contrato(
            animal=animal,
            adotante_nome=adotante_nome,
            taxa=taxa,
            strategy=strategy,
            termos=termos
        )

        return contrato

    def _gerar_contrato(
        self,
        animal: Animal,
        adotante_nome: str,
        taxa: float,
        strategy: TaxaAdocaoStrategy,
        termos: Optional[str]
    ) -> str:
        """
        Gera o texto do contrato de adoção.
        
        Args:
            animal: Animal sendo adotado.
            adotante_nome: Nome do adotante.
            taxa: Valor da taxa de adoção.
            strategy: Estratégia de taxa utilizada.
            termos: Termos adicionais (opcional).
        
        Returns:
            String formatada com o contrato completo.
        """
        agora = datetime.now(timezone.utc).isoformat()
        termos_final = termos or (
            "O adotante se compromete a zelar pelo bem-estar do animal, "
            "fornecendo alimentação adequada, cuidados veterinários e "
            "ambiente seguro."
        )

        contrato = (
            "=" * 60 + "\n"
            "CONTRATO DE ADOÇÃO\n"
            "=" * 60 + "\n"
            f"Data: {agora}\n\n"
            "DADOS DO ADOTANTE:\n"
            f"  Nome: {adotante_nome}\n\n"
            "DADOS DO ANIMAL:\n"
            f"  Nome: {animal.nome}\n"
            f"  Espécie: {animal.especie}\n"
            f"  Raça: {animal.raca}\n"
            f"  Sexo: {animal.sexo}\n"
            f"  Idade: {animal.idade_meses} meses\n"
            f"  Porte: {animal.porte}\n"
            f"  ID: {animal.id}\n\n"
            "VALORES:\n"
            f"  Taxa de Adoção: R$ {taxa:.2f}\n"
            f"  Tipo de Taxa: {strategy.nome()}\n\n"
            "TERMOS E CONDIÇÕES:\n"
            f"  {termos_final}\n\n"
            "=" * 60 + "\n"
            "Assinatura do Adotante: _______________________\n"
            "Data: ___/___/______\n"
            "=" * 60 + "\n"
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
        """
        Salva o contrato em arquivo de texto.
        
        Args:
            contrato: Texto completo do contrato.
            animal_nome: Nome do animal.
            adotante_nome: Nome do adotante.
            data_iso: Data em formato ISO8601.
        
        Returns:
            Path do arquivo criado.
        """
        # Cria pasta se não existir
        self._pasta_contratos.mkdir(parents=True, exist_ok=True)

        # Nome de arquivo seguro (remove caracteres inválidos)
        animal_safe = self._sanitizar_nome_arquivo(animal_nome)
        adotante_safe = self._sanitizar_nome_arquivo(adotante_nome)
        data_safe = data_iso.replace(":", "-").replace(".", "-")

        arquivo = (
            self._pasta_contratos / 
            f"contrato_{animal_safe}_{adotante_safe}_{data_safe}.txt"
        )
        
        arquivo.write_text(contrato, encoding="utf-8")
        return arquivo

    @staticmethod
    def _sanitizar_nome_arquivo(nome: str) -> str:
        """
        Remove caracteres inválidos de nomes de arquivo.
        
        Args:
            nome: Nome original.
        
        Returns:
            Nome sanitizado (apenas alfanuméricos, espaços, _ e -).
        """
        caracteres_validos = "".join(
            c for c in nome 
            if c.isalnum() or c in (" ", "_", "-")
        )
        return caracteres_validos.strip().replace(" ", "_")

    def __repr__(self) -> str:
        """Representação técnica do serviço."""
        return f"AdocaoService(repo={self.repo!r})"