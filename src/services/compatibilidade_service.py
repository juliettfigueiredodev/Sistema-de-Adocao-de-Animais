"""
Serviço de cálculo de compatibilidade entre adotante e animal.
"""

from src.infrastructure.settings_loader import SettingsLoader
from src.models.adotante import Adotante
from src.models.animal import Animal


class CompatibilidadeService:
    """
    Calcula o grau de compatibilidade entre um adotante e um animal.
    
    Usa pesos configuráveis do settings.json para avaliar múltiplos
    critérios e retornar um score de 0 a 100.
    
    Critérios avaliados:
    - Adequação da moradia ao porte do animal
    - Experiência prévia com pets
    - Compatibilidade com presença de crianças
    - Compatibilidade com outros animais (se houver)
    
    Attributes:
        settings: Configurações carregadas do sistema.
    
    Example:
        >>> service = CompatibilidadeService()
        >>> score = service.calcular(adotante, animal)
        >>> print(f"Compatibilidade: {score}%")
    """
    
    def __init__(self):
        """Inicializa o serviço carregando as configurações."""
        self.settings = SettingsLoader.carregar()

    def calcular(self, adotante: Adotante, animal: Animal) -> int:
        """
        Calcula a compatibilidade entre adotante e animal.
        
        O score final é calculado como a soma ponderada de vários
        critérios, com pesos definidos em settings.json.
        
        Args:
            adotante: Candidato à adoção.
            animal: Animal sendo avaliado.
        
        Returns:
            Score de compatibilidade (0-100).
        
        Example:
            >>> adotante = Adotante(
            ...     nome="João", idade=30, moradia="casa",
            ...     area_util=100, experiencia=True,
            ...     criancas=False, outros_animais=False
            ... )
            >>> animal = Cachorro(...)
            >>> score = service.calcular(adotante, animal)
            85
        """
        pesos = self.settings["compatibilidade"]["pesos"]
        score = 0.0

        # Critério 1: Adequação moradia × porte (peso: 30%)
        score += self._avaliar_moradia_porte(adotante, animal, pesos)

        # Critério 2: Experiência com pets (peso: 25%)
        score += self._avaliar_experiencia(adotante, pesos)

        # Critério 3: Compatibilidade com crianças (peso: 20%)
        score += self._avaliar_criancas(adotante, animal, pesos)

        # Critério 4: Outros animais (peso: 10%)
        if "outros_animais" in pesos:
            score += self._avaliar_outros_animais(adotante, animal, pesos)

        # Critério 5: Temperamento geral (peso: 15%)
        if "temperamento" in pesos:
            score += self._avaliar_temperamento(animal, pesos)

        # Garante que o score não ultrapasse 100
        return int(min(score, 100))

    def _avaliar_moradia_porte(
        self, 
        adotante: Adotante, 
        animal: Animal, 
        pesos: dict
    ) -> float:
        """
        Avalia adequação da moradia ao porte do animal.
        
        Args:
            adotante: Adotante com tipo de moradia.
            animal: Animal com porte.
            pesos: Dicionário de pesos.
        
        Returns:
            Pontos obtidos neste critério (0-30).
        """
        peso = pesos.get("porte_moradia", 0.30)  # 30% por padrão
        
        # Porte Grande: ideal ter casa
        if animal.porte == "G":
            if adotante.moradia == "casa":
                return peso * 100  # 100% dos 30 pontos = 30
            else:
                return peso * 50   # 50% dos 30 pontos = 15
        
        # Portes P e M: qualquer moradia é adequada
        return peso * 100  # 30 pontos

    def _avaliar_experiencia(self, adotante: Adotante, pesos: dict) -> float:
        """
        Avalia experiência prévia com pets.
        
        Args:
            adotante: Adotante com flag de experiência.
            pesos: Dicionário de pesos.
        
        Returns:
            Pontos obtidos neste critério (0-25).
        """
        peso = pesos.get("experiencia", 0.25)  # 25% por padrão
        
        if adotante.experiencia:
            return peso * 100  # 100% dos 25 pontos = 25
        else:
            return peso * 60   # 60% dos 25 pontos = 15

    def _avaliar_criancas(
        self, 
        adotante: Adotante, 
        animal: Animal, 
        pesos: dict
    ) -> float:
        """
        Avalia compatibilidade com presença de crianças.
        
        Animais com temperamento 'arisco' são penalizados se
        houver crianças na casa.
        
        Args:
            adotante: Adotante com flag de crianças.
            animal: Animal com temperamento.
            pesos: Dicionário de pesos.
        
        Returns:
            Pontos obtidos neste critério (0-20).
        """
        peso = pesos.get("criancas", 0.20)  # 20% por padrão
        
        # Se não tem crianças, não há problema
        if not adotante.criancas:
            return peso * 100  # 20 pontos
        
        # Se tem crianças E animal é arisco: PENALIZA
        if "arisco" in animal.temperamento:
            return peso * 20   # 20% dos 20 pontos = 4
        
        # Tem crianças mas animal não é arisco: OK
        return peso * 100  # 20 pontos

    def _avaliar_outros_animais(
        self, 
        adotante: Adotante, 
        animal: Animal, 
        pesos: dict
    ) -> float:
        """
        Avalia compatibilidade com outros animais na casa.
        
        Args:
            adotante: Adotante com flag de outros animais.
            animal: Animal com temperamento.
            pesos: Dicionário de pesos.
        
        Returns:
            Pontos obtidos neste critério (0-10).
        """
        peso = pesos.get("outros_animais", 0.10)  # 10% por padrão
        
        # Se não tem outros animais, não há problema
        if not adotante.outros_animais:
            return peso * 100  # 10 pontos
        
        # Se tem outros animais E este é "sociavel": BONUS
        if "sociavel" in animal.temperamento:
            return peso * 100  # 10 pontos
        
        # Tem outros animais mas animal não é sociável: PENALIZA
        return peso * 50  # 5 pontos

    def _avaliar_temperamento(self, animal: Animal, pesos: dict) -> float:
        """
        Avalia temperamento geral do animal.
        
        Animais com temperamento "docil" ou "calmo" ganham pontos extras.
        
        Args:
            animal: Animal com temperamento.
            pesos: Dicionário de pesos.
        
        Returns:
            Pontos obtidos neste critério (0-15).
        """
        peso = pesos.get("temperamento", 0.15)  # 15% por padrão
        
        temperamentos_positivos = {"docil", "calmo", "tranquilo", "sociavel"}
        
        # Verifica se tem algum temperamento positivo
        if any(t in animal.temperamento for t in temperamentos_positivos):
            return peso * 100  # 15 pontos
        
        # Temperamento neutro
        return peso * 70  # 10.5 pontos

    def __repr__(self) -> str:
        """Representação técnica do serviço."""
        return "CompatibilidadeService()"