from src.models.pessoa import Pessoa # Importa a classe Pessoa do módulo pessoa

class Adotante(Pessoa): # Define a classe Adotante que herda de Pessoa
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
        super().__init__(nome, idade) # Chama o construtor da classe base Pessoa
        self.moradia = moradia
        self.area_util = area_util
        self.experiencia = experiencia
        self.criancas = criancas
        self.outros_animais = outros_animais