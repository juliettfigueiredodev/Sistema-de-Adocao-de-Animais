from src.validators.politica_triagem import PoliticaTriagem
from src.services.compatibilidade_service import CompatibilidadeService


class TriagemService:
    """
    Serviço que centraliza a validação do adotante
    e o cálculo de compatibilidade com o animal.
    """

    def __init__(self):
        self.politica = PoliticaTriagem()
        self.compatibilidade = CompatibilidadeService()

    def avaliar(self, adotante, animal) -> int:
        """
        Valida o adotante e retorna o score de compatibilidade.
        """
        self.politica.validar(adotante, animal.porte)
        return self.compatibilidade.calcular(adotante, animal)
