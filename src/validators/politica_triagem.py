from src.infrastructure.settings_loader import SettingsLoader
from src.validators.exceptions import PoliticaNaoAtendidaError
from src.models.adotante import Adotante

class PoliticaTriagem:
    def __init__(self):
        '''Carrega as regras de triagem definidas no arquivo de configurações'''
        self.settings = SettingsLoader.carregar()

    def validar(self, adotante: Adotante, porte_animal: str | None = None) -> None:
        '''Recupera as políticas gerais do sistema'''
        politicas = self.settings["politicas"]

        '''Verifica se o adotante possui idade mínima'''
        if adotante.idade < politicas["idade_minima"]:
            raise PoliticaNaoAtendidaError(
                "Adotante não possui idade mínima para adoção."
            )

        '''Regras específicas para animais de grande porte'''
        if porte_animal == "G":
            '''Exige moradia do tipo casa'''
            if adotante.moradia != "casa":
                raise PoliticaNaoAtendidaError(
                    "Animais de grande porte exigem moradia do tipo casa."
                )

            '''Verifica se a área da moradia é suficiente'''
            if adotante.area_util < politicas["area_minima_porte_g"]:
                raise PoliticaNaoAtendidaError(
                    "Área da moradia insuficiente para animal de grande porte."
                )
