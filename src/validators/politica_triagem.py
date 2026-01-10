"""
Módulo responsável pela validação de políticas de triagem.
"""

from src.infrastructure.settings_loader import SettingsLoader
from src.validators.exceptions import PoliticaNaoAtendidaError
from src.models.adotante import Adotante


class PoliticaTriagem:
    """
    Valida se adotantes atendem às políticas de triagem do sistema.
    
    As políticas são carregadas do arquivo settings.json e incluem:
    - Idade mínima do adotante
    - Restrições de moradia por porte do animal
    - Área mínima necessária
    
    Attributes:
        settings: Configurações carregadas do sistema.
    
    Example:
        >>> politica = PoliticaTriagem()
        >>> politica.validar(adotante, "G")
    """
    
    def __init__(self):
        """Inicializa o validador carregando as configurações."""
        self.settings = SettingsLoader.carregar()
    
    def validar(
        self, 
        adotante: Adotante, 
        porte_animal: str | None = None
    ) -> None:
        """
        Valida se o adotante atende às políticas de triagem.
        
        Verifica:
        1. Idade mínima do adotante
        2. Para animais de grande porte:
           - Tipo de moradia adequado
           - Área mínima necessária
        
        Args:
            adotante: Candidato à adoção a ser validado.
            porte_animal: Porte do animal (P/M/G). Se None, ignora validações de porte.
        
        Raises:
            PoliticaNaoAtendidaError: Se alguma política não for atendida.
        
        Example:
            >>> politica = PoliticaTriagem()
            >>> try:
            ...     politica.validar(adotante, "G")
            ... except PoliticaNaoAtendidaError as e:
            ...     print(f"Rejeitado: {e}")
        """
        politicas = self.settings["politicas"]
        
        # Validação 1: Idade mínima
        if adotante.idade < politicas["idade_minima"]:
            raise PoliticaNaoAtendidaError(
                f"Adotante deve ter no mínimo {politicas['idade_minima']} anos. "
                f"Idade atual: {adotante.idade} anos."
            )
        
        # Validação 2: Regras específicas para porte grande
        if porte_animal == "G":
            moradia_necessaria = politicas.get(
                "moradia_permitida_porte_g", 
                "casa"
            )
            
            if adotante.moradia != moradia_necessaria:
                raise PoliticaNaoAtendidaError(
                    f"Animais de grande porte exigem moradia do tipo '{moradia_necessaria}'. "
                    f"Moradia atual: {adotante.moradia}."
                )
            
            area_minima = politicas["area_minima_porte_g"]
            if adotante.area_util < area_minima:
                raise PoliticaNaoAtendidaError(
                    f"Área da moradia insuficiente para animal de grande porte. "
                    f"Necessário: {area_minima}m², disponível: {adotante.area_util}m²."
                )
    
    def __repr__(self) -> str:
        """Representação técnica do validador."""
        return "PoliticaTriagem()"