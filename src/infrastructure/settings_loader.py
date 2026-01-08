import json
from typing import Dict


class SettingsLoader:
    """
    Responsável por carregar as configurações do sistema
    a partir do arquivo settings.json.
    """

    @staticmethod
    def carregar() -> Dict:
        """
        Retorna as configurações como dicionário.
        """
        with open("settings.json", "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
