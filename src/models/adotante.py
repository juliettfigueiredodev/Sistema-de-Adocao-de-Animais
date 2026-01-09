"""
Módulo contendo a classe Adotante.
"""

from typing import Literal
from src.models.pessoa import Pessoa


class Adotante(Pessoa):
    """
    Representa uma pessoa interessada em adotar um animal.
    
    Estende a classe Pessoa adicionando informações necessárias
    para triagem e cálculo de compatibilidade.
    
    Attributes:
        nome: Nome completo do adotante.
        idade: Idade do adotante em anos.
        moradia: Tipo de moradia (casa ou apartamento).
        area_util: Área útil da moradia em metros quadrados.
        experiencia: Se o adotante tem experiência prévia com pets.
        criancas: Se há crianças na residência.
        outros_animais: Se já possui outros animais.
    
    Example:
        >>> adotante = Adotante(
        ...     nome="Maria Santos",
        ...     idade=28,
        ...     moradia="casa",
        ...     area_util=80,
        ...     experiencia=True,
        ...     criancas=False,
        ...     outros_animais=True
        ... )
        >>> print(adotante)
        Adotante: Maria Santos, 28 anos, casa de 80m²
    """
    
    def __init__(
        self,
        nome: str,
        idade: int,
        moradia: Literal["casa", "apartamento"],
        area_util: int,
        experiencia: bool,
        criancas: bool,
        outros_animais: bool
    ):
        """
        Inicializa um novo adotante.
        
        Args:
            nome: Nome completo do adotante.
            idade: Idade em anos.
            moradia: Tipo de moradia ("casa" ou "apartamento").
            area_util: Área útil da moradia em m².
            experiencia: Se tem experiência com pets.
            criancas: Se há crianças na residência.
            outros_animais: Se já possui outros animais.
        
        Raises:
            ValueError: Se área for negativa ou moradia inválida.
        """
        super().__init__(nome, idade)
        
        if moradia not in ("casa", "apartamento"):
            raise ValueError(f"Moradia inválida: {moradia}")
        if area_util <= 0:
            raise ValueError(f"Área útil deve ser positiva: {area_util}")
        
        self._moradia = moradia
        self._area_util = area_util
        self.experiencia = experiencia
        self.criancas = criancas
        self.outros_animais = outros_animais
    
    @property
    def moradia(self) -> str:
        """Tipo de moradia (casa ou apartamento)."""
        return self._moradia
    
    @property
    def area_util(self) -> int:
        """Área útil da moradia em metros quadrados."""
        return self._area_util
    
    @area_util.setter
    def area_util(self, valor: int) -> None:
        """
        Define a área útil com validação.
        
        Args:
            valor: Nova área em m².
        
        Raises:
            ValueError: Se a área for não-positiva.
        """
        if valor <= 0:
            raise ValueError(f"Área útil deve ser positiva: {valor}")
        self._area_util = valor
    
    def __str__(self) -> str:
        """
        Retorna representação amigável do adotante.
        
        Returns:
            String formatada com dados principais do adotante.
        """
        return (
            f"Adotante: {self.nome}, {self.idade} anos, "
            f"{self.moradia} de {self.area_util}m²"
        )
    
    def __repr__(self) -> str:
        """
        Retorna representação técnica do adotante.
        
        Returns:
            String com todos os atributos do adotante.
        """
        return (
            f"Adotante(nome={self.nome!r}, idade={self.idade}, "
            f"moradia={self.moradia!r}, area_util={self.area_util}, "
            f"experiencia={self.experiencia}, criancas={self.criancas}, "
            f"outros_animais={self.outros_animais})"
        )