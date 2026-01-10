"""
Repositório de persistência de animais em JSON.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from src.models.animal import Animal
from src.models.animal_status import AnimalStatus
from src.models.cachorro import Cachorro
from src.models.gato import Gato


class AnimalNaoEncontradoError(LookupError):
    """
    Exceção lançada quando um animal não é encontrado no repositório.
    
    Example:
        >>> raise AnimalNaoEncontradoError("Animal abc-123 não encontrado")
    """
    pass


class AnimalDuplicadoError(ValueError):
    """
    Exceção lançada ao tentar adicionar animal com ID já existente.
    
    Example:
        >>> raise AnimalDuplicadoError("Já existe animal com ID abc-123")
    """
    pass


def animal_from_dict(data: Dict) -> Animal:
    """
    Factory method para criar instâncias de Animal a partir de dicionário.
    
    Deserializa dados JSON e cria a instância apropriada (Cachorro ou Gato)
    baseado no campo 'especie'.
    
    Args:
        data: Dicionário com dados do animal (geralmente de JSON).
    
    Returns:
        Instância de Cachorro ou Gato.
    
    Raises:
        ValueError: Se a espécie for desconhecida ou dados estiverem inválidos.
    
    Example:
        >>> data = {
        ...     "id": "abc-123",
        ...     "especie": "Cachorro",
        ...     "nome": "Rex",
        ...     ...
        ... }
        >>> animal = animal_from_dict(data)
        >>> isinstance(animal, Cachorro)
        True
    """
    # Converte status
    status = AnimalStatus(data["status"])
    reservado_por = data.get("reservado_por")
    reserva_ate = data.get("reserva_ate")
    
    # Validação: Se vier RESERVADO no JSON mas faltar dados da reserva,
    # corrige para DISPONIVEL (dados inconsistentes)
    if status == AnimalStatus.RESERVADO and (not reservado_por or not reserva_ate):
        print(
            f"[AVISO] Animal {data.get('id')} está RESERVADO mas faltam "
            f"dados de reserva. Corrigindo para DISPONIVEL."
        )
        status = AnimalStatus.DISPONIVEL
        reservado_por = None
        reserva_ate = None

    # Identifica espécie e cria instância apropriada
    especie = data.get("especie")
    
    if especie == "Cachorro":
        return Cachorro(
            raca=data["raca"],
            nome=data["nome"],
            sexo=data["sexo"],
            idade_meses=int(data["idade_meses"]),
            porte=data["porte"],
            necessidade_passeio=int(data.get("necessidade_passeio", 5)),
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
            independencia=int(data.get("independencia", 5)),
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
    Repositório de persistência de animais em arquivo JSON.
    
    Gerencia o armazenamento em memória e persistência em disco
    de todos os animais do sistema.
    
    Attributes:
        _path: Caminho do arquivo JSON de persistência.
        _animais: Dicionário interno de animais (id -> Animal).
    
    Example:
        >>> repo = AnimalRepository("data/animais.json")
        >>> repo.load()  # Carrega dados do arquivo
        >>> 
        >>> cachorro = Cachorro(...)
        >>> repo.add(cachorro)
        >>> repo.save()  # Persiste no arquivo
        >>> 
        >>> animal = repo.get(cachorro.id)
        >>> print(animal.nome)
    """
    
    def __init__(self, arquivo_json: str = "data/animais.json") -> None:
        """
        Inicializa o repositório.
        
        Args:
            arquivo_json: Caminho para o arquivo JSON de persistência.
        """
        self._path = Path(arquivo_json)
        self._animais: Dict[str, Animal] = {}

    # CRUD - Create, Read, Update, Delete

    def add(self, animal: Animal) -> None:
        """
        Adiciona um novo animal ao repositório.
        
        Args:
            animal: Animal a ser adicionado.
        
        Raises:
            AnimalDuplicadoError: Se já existir animal com o mesmo ID.
        
        Example:
            >>> cachorro = Cachorro(...)
            >>> repo.add(cachorro)
        """
        if animal.id in self._animais:
            raise AnimalDuplicadoError(
                f"Já existe animal com ID {animal.id}"
            )
        self._animais[animal.id] = animal

    def get(self, animal_id: str) -> Optional[Animal]:
        """
        Busca um animal por ID.
        
        Args:
            animal_id: ID único do animal.
        
        Returns:
            Animal encontrado, ou None se não existir.
        
        Example:
            >>> animal = repo.get("abc-123")
            >>> if animal:
            ...     print(animal.nome)
        """
        return self._animais.get(animal_id)

    def get_or_raise(self, animal_id: str) -> Animal:
        """
        Busca um animal por ID, lançando exceção se não existir.
        
        Args:
            animal_id: ID único do animal.
        
        Returns:
            Animal encontrado.
        
        Raises:
            AnimalNaoEncontradoError: Se o animal não existir.
        
        Example:
            >>> try:
            ...     animal = repo.get_or_raise("abc-123")
            ... except AnimalNaoEncontradoError:
            ...     print("Animal não encontrado")
        """
        if animal_id not in self._animais:
            raise AnimalNaoEncontradoError(
                f"Animal não encontrado: {animal_id}"
            )
        return self._animais[animal_id]

    def exists(self, animal_id: str) -> bool:
        """
        Verifica se um animal existe no repositório.
        
        Args:
            animal_id: ID único do animal.
        
        Returns:
            True se existir, False caso contrário.
        
        Example:
            >>> if repo.exists("abc-123"):
            ...     print("Animal existe")
        """
        return animal_id in self._animais

    def update(self, animal: Animal) -> None:
        """
        Atualiza os dados de um animal existente.
        
        Args:
            animal: Animal com dados atualizados.
        
        Raises:
            AnimalNaoEncontradoError: Se o animal não existir.
        
        Example:
            >>> animal = repo.get("abc-123")
            >>> animal.nome = "Novo Nome"
            >>> repo.update(animal)
        """
        if animal.id not in self._animais:
            raise AnimalNaoEncontradoError(
                f"Animal não encontrado para atualização: {animal.id}"
            )
        self._animais[animal.id] = animal

    def delete(self, animal_id: str) -> None:
        """
        Remove um animal do repositório.
        
        Args:
            animal_id: ID único do animal a ser removido.
        
        Raises:
            AnimalNaoEncontradoError: Se o animal não existir.
        
        Example:
            >>> repo.delete("abc-123")
        """
        if animal_id not in self._animais:
            raise AnimalNaoEncontradoError(
                f"Animal não encontrado para exclusão: {animal_id}"
            )
        del self._animais[animal_id]

    def list(
        self,
        status: Optional[AnimalStatus] = None,
        especie: Optional[str] = None,
        porte: Optional[str] = None,
    ) -> List[Animal]:
        """
        Lista animais com filtros opcionais.
        
        Args:
            status: Filtrar por status (ex: DISPONIVEL, RESERVADO).
            especie: Filtrar por espécie (ex: "Cachorro", "Gato").
            porte: Filtrar por porte (ex: "P", "M", "G").
        
        Returns:
            Lista de animais ordenada por data de entrada (mais antigos primeiro).
        
        Example:
            >>> # Todos os cachorros disponíveis de porte grande
            >>> disponiveis = repo.list(
            ...     status=AnimalStatus.DISPONIVEL,
            ...     especie="Cachorro",
            ...     porte="G"
            ... )
        """
        animais = list(self._animais.values())
        
        # Aplica filtros
        if status is not None:
            animais = [a for a in animais if a.status == status]
        if especie is not None:
            animais = [a for a in animais if a.especie == especie]
        if porte is not None:
            animais = [a for a in animais if a.porte == porte]
        
        # Ordena por data_entrada (usa __lt__ do Animal)
        return sorted(animais)

    def count(
        self,
        status: Optional[AnimalStatus] = None,
        especie: Optional[str] = None,
    ) -> int:
        """
        Conta animais com filtros opcionais.
        
        Args:
            status: Filtrar por status.
            especie: Filtrar por espécie.
        
        Returns:
            Quantidade de animais que atendem aos filtros.
        
        Example:
            >>> total_disponiveis = repo.count(status=AnimalStatus.DISPONIVEL)
        """
        return len(self.list(status=status, especie=especie))

    # Persistência

    def load(self) -> None:
        """
        Carrega dados do arquivo JSON para a memória.
        
        Se o arquivo não existir, o repositório permanece vazio.
        
        Raises:
            json.JSONDecodeError: Se o arquivo contiver JSON inválido.
        
        Example:
            >>> repo = AnimalRepository()
            >>> repo.load()
            >>> print(f"Carregados {len(repo)} animais")
        """
        if not self._path.exists():
            print(f"[INFO] Arquivo {self._path} não encontrado. Iniciando vazio.")
            return

        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Erro ao decodificar JSON em {self._path}: {e.msg}",
                e.doc,
                e.pos
            )

        self._animais.clear()
        
        for item in raw:
            try:
                animal = animal_from_dict(item)
                self._animais[animal.id] = animal
            except Exception as e:
                print(
                    f"[ERRO] Falha ao carregar animal {item.get('id', '?')}: {e}"
                )
                continue

        print(f"[INFO] Carregados {len(self._animais)} animais de {self._path}")

    def save(self) -> None:
        """
        Salva o estado atual em arquivo JSON.
        
        Cria o diretório pai se não existir.
        
        Example:
            >>> repo.add(cachorro)
            >>> repo.save()  # Persiste no disco
        """
        # Cria diretório se não existir
        self._path.parent.mkdir(parents=True, exist_ok=True)
        
        # Serializa todos os animais
        data = [a.to_dict() for a in self._animais.values()]
        
        # Escreve JSON formatado
        self._path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        
        print(f"[INFO] Salvos {len(self._animais)} animais em {self._path}")

    def clear(self) -> None:
        """
        Remove todos os animais da memória (não afeta o arquivo).
        
        Example:
            >>> repo.clear()
            >>> len(repo)
            0
        """
        self._animais.clear()

    # Métodos especiais

    def __len__(self) -> int:
        """
        Retorna quantidade de animais no repositório.
        
        Returns:
            Número de animais.
        
        Example:
            >>> len(repo)
            42
        """
        return len(self._animais)

    def __iter__(self):
        """
        Permite iterar sobre os animais.
        
        Returns:
            Iterador sobre os valores (animais).
        
        Example:
            >>> for animal in repo:
            ...     print(animal.nome)
        """
        return iter(self._animais.values())

    def __repr__(self) -> str:
        """
        Representação técnica do repositório.
        
        Returns:
            String com informações do repositório.
        """
        return (
            f"AnimalRepository(arquivo={self._path}, "
            f"total_animais={len(self._animais)})"
        )

    def __str__(self) -> str:
        """
        Representação amigável do repositório.
        
        Returns:
            String com estatísticas resumidas.
        """
        disponiveis = self.count(status=AnimalStatus.DISPONIVEL)
        reservados = self.count(status=AnimalStatus.RESERVADO)
        adotados = self.count(status=AnimalStatus.ADOTADO)
        
        return (
            f"AnimalRepository: {len(self)} animais total\n"
            f"  - {disponiveis} disponíveis\n"
            f"  - {reservados} reservados\n"
            f"  - {adotados} adotados"
        )