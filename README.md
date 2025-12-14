# Sistema-de-Adocao-de-Animais
Projeto final da disciplina de POO

## Type hints
Anotações de sintaxe para indicar o tipo de dado esperado para variáveis, parâmetros de funções e retornos de funções.
Exemplos (criado por IA via busca no campo de pesquisa Google):

```
idade: int = 25
nome: str = "Maria"
saldo: float = 1500.75
is_ativo: bool = True


def saudacao(nome: str) -> str:
    """Retorna uma string de saudação."""
    return f"Olá, {nome}!"

def somar(a: int, b: int) -> int:
    """Soma dois números inteiros e retorna o resultado."""
    return a + b

from typing import List, Dict

nomes: List[str] = ["João", "Ana", "Carlos"]
configuracoes: Dict[str, str] = {"tema": "escuro", "idioma": "portugues"}

```

## Docstrings

O docstring é uma string de documentação que deve aparecer dentro do código-fonte da classe, método ou módulo que está sendo documentado. Exemplo estilo google e estilo numpy abaixo criados por Gemini.

### Estilo  Google

```
class Cachorro(Animal, VacinavelMixin, AdestravelMixin):
    """Representa um cão no sistema de adoção.

    Herda de Animal e implementa funcionalidades específicas de cães
    como vacinação e adestramento através de Mixins.
    Cachorros possuem atributos específicos como a necessidade de passeio. [cite: 37]

    Attributes:
        necessidade_passeio (str): Nível de necessidade de exercícios/passeio
            (ex: 'Baixa', 'Média', 'Alta'). [cite: 37]
        _agenda_vacinas (list): Lista de datas de vacinas pendentes. (Herdado de VacinavelMixin) [cite: 39]
        _nivel_adestramento (int): Nível de adestramento do cão (0-10). (Herdado de AdestravelMixin) [cite: 40]
        id (str): Identificador único do animal. [cite: 46]
        especie (str): Espécie do animal (sempre 'Cachorro'). [cite: 11]
        status (str): Estado atual do animal (ex: 'DISPONIVEL', 'RESERVADO', 'QUARENTENA'). [cite: 12]
        # Outros atributos herdados...
    """

    def __init__(self, raca: str, nome: str, sexo: str, idade_meses: int, porte: str,
                 temperamento: list, necessidade_passeio: str):
        """Inicializa uma nova instância de Cachorro.

        Args:
            raca (str): Raça específica do cão. [cite: 11]
            nome (str): Nome do cão. [cite: 11]
            sexo (str): Sexo do cão. [cite: 11]
            idade_meses (int): Idade do cão em meses (≥ 0). [cite: 11, 43]
            porte (str): Porte do cão ('P', 'M', 'G'). [cite: 11, 43]
            temperamento (list): Lista de características de temperamento. [cite: 11]
            necessidade_passeio (str): Nível de necessidade de passeio. [cite: 37]
        
        Raises:
            ValueError: Se a idade for negativa ou o porte for inválido. [cite: 43]
        """
        # ... implementação

    def vacinar(self, vacina: str):
        """Registra a aplicação de uma vacina e atualiza o histórico.

        Args:
            vacina (str): O nome da vacina aplicada. [cite: 39]

        Returns:
            bool: True se a vacina foi registrada com sucesso.
        """
        # ... implementação

    def treinar(self, ganho_nivel: int = 1):
        """Aumenta o nível de adestramento do cão.

        Args:
            ganho_nivel (int): Quantidade de níveis para aumentar. Padrão é 1. [cite: 40]
        """
        # ... implementação
```

### Estilo Numpy

```
class Cachorro(Animal, VacinavelMixin, AdestravelMixin):
    """Representa um cão no sistema de adoção.

    Hereda de Animal e implementa funcionalidades específicas de cães
    como vacinação e adestramento através de Mixins.
    Cachorros possuem atributos específicos como a necessidade de passeio. [cite: 37]

    Attributes
    ----------
    necessidade_passeio : str
        Nível de necessidade de exercícios/passeio (ex: 'Baixa', 'Média', 'Alta'). [cite: 37]
    _agenda_vacinas : list
        Lista de datas de vacinas pendentes. (Herdado de VacinavelMixin) [cite: 39]
    _nivel_adestramento : int
        Nível de adestramento do cão (0-10). (Herdado de AdestravelMixin) [cite: 40]
    id : str
        Identificador único do animal. [cite: 46]
    especie : str
        Espécie do animal (sempre 'Cachorro'). [cite: 11]
    status : str
        Estado atual do animal (ex: 'DISPONIVEL', 'RESERVADO', 'QUARENTENA'). [cite: 12]
    # Outros atributos herdados...
    """

    def __init__(self, raca: str, nome: str, sexo: str, idade_meses: int, porte: str,
                 temperamento: list, necessidade_passeio: str):
        """Inicializa uma nova instância de Cachorro.

        Parameters
        ----------
        raca : str
            Raça específica do cão. [cite: 11]
        nome : str
            Nome do cão. [cite: 11]
        sexo : str
            Sexo do cão. [cite: 11]
        idade_meses : int
            Idade do cão em meses (≥ 0). [cite: 11, 43]
        porte : str
            Porte do cão ('P', 'M', 'G'). [cite: 11, 43]
        temperamento : list
            Lista de características de temperamento. [cite: 11]
        necessidade_passeio : str
            Nível de necessidade de passeio. [cite: 37]
        
        Raises
        ------
        ValueError
            Se a idade for negativa ou o porte for inválido. [cite: 43]
        """
        # ... implementação

    def vacinar(self, vacina: str) -> bool:
        """Registra a aplicação de uma vacina e atualiza o histórico.

        Parameters
        ----------
        vacina : str
            O nome da vacina aplicada. [cite: 39]

        Returns
        -------
        bool
            True se a vacina foi registrada com sucesso.
        """
        # ... implementação

    def treinar(self, ganho_nivel: int = 1):
        """Aumenta o nível de adestramento do cão.

        Parameters
        ----------
        ganho_nivel : int, optional
            Quantidade de níveis para aumentar. Padrão é 1. [cite: 40]
        """
        # ... implementação
```

