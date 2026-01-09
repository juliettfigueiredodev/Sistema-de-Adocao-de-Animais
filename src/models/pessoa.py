"""
Módulo contendo a classe base Pessoa.
"""

from typing import Any


class Pessoa:
    """
    Classe base que representa uma pessoa no sistema.
    
    Attributes:
        nome: Nome completo da pessoa.
        idade: Idade da pessoa em anos.
    
    Example:
        >>> pessoa = Pessoa("João Silva", 30)
        >>> print(pessoa)
        João Silva (30 anos)
    """
    
    def __init__(self, nome: str, idade: int):
        """
        Inicializa uma nova pessoa.
        
        Args:
            nome: Nome completo da pessoa.
            idade: Idade em anos (deve ser não-negativa).
        
        Raises:
            ValueError: Se idade for negativa ou nome vazio.
        """
        if not nome or not nome.strip():
            raise ValueError("Nome não pode ser vazio")
        if idade < 0:
            raise ValueError(f"Idade não pode ser negativa: {idade}")
        
        self._nome = nome.strip()
        self._idade = idade
    
    @property
    def nome(self) -> str:
        """Nome da pessoa."""
        return self._nome
    
    @property
    def idade(self) -> int:
        """Idade da pessoa em anos."""
        return self._idade
    
    @idade.setter
    def idade(self, valor: int) -> None:
        """
        Define a idade da pessoa com validação.
        
        Args:
            valor: Nova idade em anos.
        
        Raises:
            ValueError: Se a idade for negativa.
        """
        if valor < 0:
            raise ValueError(f"Idade não pode ser negativa: {valor}")
        self._idade = valor
    
    def __str__(self) -> str:
        """
        Retorna representação amigável da pessoa.
        
        Returns:
            String no formato "Nome (idade anos)".
        """
        return f"{self.nome} ({self.idade} anos)"
    
    def __repr__(self) -> str:
        """
        Retorna representação técnica da pessoa.
        
        Returns:
            String no formato "Pessoa(nome='...', idade=...)".
        """
        return f"Pessoa(nome={self.nome!r}, idade={self.idade})"
    
    def __eq__(self, other: Any) -> bool:
        """
        Compara igualdade entre pessoas.
        
        Duas pessoas são consideradas iguais se possuem
        o mesmo nome e idade.
        
        Args:
            other: Objeto a ser comparado.
        
        Returns:
            True se forem iguais, False caso contrário.
        """
        if not isinstance(other, Pessoa):
            return NotImplemented
        return self.nome == other.nome and self.idade == other.idade
    
    def __hash__(self) -> int:
        """
        Retorna hash da pessoa para uso em sets/dicts.
        
        Returns:
            Hash baseado em nome e idade.
        """
        return hash((self.nome, self.idade))