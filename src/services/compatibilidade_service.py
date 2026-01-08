from src.infrastructure.settings_loader import SettingsLoader


class CompatibilidadeService:
    """
    Serviço responsável por calcular o grau de compatibilidade
    entre um adotante e um animal.
    """

    def __init__(self):
        self.settings = SettingsLoader.carregar()

    def calcular(self, adotante, animal) -> int:
        """
        Calcula a compatibilidade com base em pesos
        definidos nas configurações do sistema.
        """
        pesos = self.settings["compatibilidade"]["pesos"]
        score = 0

        if animal.porte == "G":
            if adotante.moradia == "casa":
                score += pesos["porte_moradia"]
        else:
            score += pesos["porte_moradia"]

        if adotante.experiencia:
            score += pesos["experiencia"]
        else:
            score += pesos["experiencia"] // 2

        if adotante.criancas and "arisco" in animal.temperamento:
            score += 0
        else:
            score += pesos["criancas"]

        return min(score, 100)
