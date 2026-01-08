from src.models.pessoa import Pessoa


class Adotante(Pessoa):
    """
    Representa uma pessoa interessada em adotar um animal.

    Estende a classe Pessoa adicionando informações
    necessárias para triagem e compatibilidade.
    """

    def __init__(
        self,
        nome: str,
        idade: int,
        moradia: str,
        area_util: int,
        experiencia: bool,
        criancas: bool,
        outros_animais: bool
    ):
        super().__init__(nome, idade)
        self.moradia = moradia
        self.area_util = area_util
        self.experiencia = experiencia
        self.criancas = criancas
        self.outros_animais = outros_animais
