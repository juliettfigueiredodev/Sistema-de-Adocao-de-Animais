import json # Biblioteca para ler e converter arquivos JSON
from typing import Dict

class SettingsLoader:
    # Classe responsável por carregar as configurações do sistema

    @staticmethod
    def carregar() -> Dict:
        # Abre o arquivo settings.json e lê seu conteúdo
        with open("settings.json", "r", encoding="utf-8") as arquivo:
            # Converte o JSON em um dicionário Python e retorna
            return json.load(arquivo)

