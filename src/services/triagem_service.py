"""
Serviço de triagem de adotantes.
"""

from src.infrastructure.settings_loader import SettingsLoader
from src.models.adotante import Adotante
from src.models.animal import Animal
from src.services.compatibilidade_service import CompatibilidadeService
from src.validators.politica_triagem import PoliticaTriagem


class TriagemService:
    """
    Centraliza a validação de adotantes e cálculo de compatibilidade.
    
    Combina validação de políticas (idade mínima, moradia adequada)
    com cálculo de score de compatibilidade.
    
    Attributes:
        politica: Validador de políticas de triagem.
        compatibilidade: Calculador de score de compatibilidade.
    
    Example:
        >>> service = TriagemService()
        >>> try:
        ...     score = service.avaliar(adotante, animal)
        ...     print(f"Aprovado! Score: {score}")
        ... except PoliticaNaoAtendidaError as e:
        ...     print(f"Reprovado: {e}")
    """
    
    def __init__(self):
        """
        Inicializa o serviço de triagem.
        
        Cria instâncias de PoliticaTriagem e CompatibilidadeService.
        """
        self.politica = PoliticaTriagem()
        self.compatibilidade = CompatibilidadeService()

    def avaliar(self, adotante: Adotante, animal: Animal) -> int:
        """
        Avalia um adotante para um animal específico.
        
        Primeiro valida se o adotante atende às políticas obrigatórias.
        Se passar, calcula e retorna o score de compatibilidade.
        
        Args:
            adotante: Candidato à adoção a ser avaliado.
            animal: Animal para o qual calcular compatibilidade.
        
        Returns:
            Score de compatibilidade (0-100).
        
        Raises:
            PoliticaNaoAtendidaError: Se o adotante não atender às políticas.
        
        Example:
            >>> adotante = Adotante(
            ...     nome="Maria", idade=25, moradia="casa",
            ...     area_util=80, experiencia=True,
            ...     criancas=False, outros_animais=False
            ... )
            >>> animal = Cachorro(nome="Rex", porte="G", ...)
            >>> score = service.avaliar(adotante, animal)
            85
        """
        # Passo 1: Valida políticas obrigatórias
        # (lança exceção se não atender)
        self.politica.validar(adotante, animal.porte)
        
        # Passo 2: Calcula compatibilidade
        score = self.compatibilidade.calcular(adotante, animal)
        
        return score

    def __repr__(self) -> str:
        """Representação técnica do serviço."""
        return (
            f"TriagemService(politica={self.politica!r}, "
            f"compatibilidade={self.compatibilidade!r})"
        )
