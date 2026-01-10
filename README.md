# Sobre o Projeto

Sistema para gerenciar todo o fluxo de adoção de animais, incluindo cadastro, triagem de adotantes, reservas, adoções e relatórios estatísticos.

**Principais funcionalidades:**
- Cadastro de animais (cachorros e gatos) com validações
- Triagem automática de adotantes por políticas configuráveis
- Sistema de reservas com expiração automática
- Cálculo de compatibilidade adotante-animal (score 0-100)
- Geração de contratos de adoção com diferentes estratégias de taxa
- Relatórios estatísticos

## Sistema de Adoção de Animais
Projeto final da disciplina de POO 

<img width="631" height="546" alt="image" src="https://github.com/user-attachments/assets/b7df48ba-dbad-4248-b1dd-bb643c79a1f5" />


## Como Usar

### Pré-requisitos
```bash
Python 3.10+
Pytest
```

### Instalação
```bash
git clone [https://github.com/juliettfigueiredodev/Sistema-de-Adocao-de-Animais.git]
cd sistema-adocao-animais
pip install pytest
```

### Tecnologias Utilizadas

- [Python 3.x](https://www.python.org/) — linguagem utilizada no backend da aplicação.
- [Git](https://git-scm.com/) — controle de versão do código-fonte.
- [GitHub](https://github.com/) — hospedagem do repositório e colaboração entre os membros do time.
- [VS Code](https://code.visualstudio.com/) — editor de código utilizado no desenvolvimento.
- [Pytest](https://docs.pytest.org/en/stable/) — framework utilizado para a criação e execução de testes automatizados, garantindo a qualidade e o correto funcionamento da aplicação.

##  Conceitos de POO

- **Herança:** Animal → Cachorro/Gato, Pessoa → Adotante
- **Encapsulamento:** @property com validações
- **Polimorfismo:** Estratégias de taxa intercambiáveis
- **Abstração:** Classes abstratas (Animal, TaxaAdocaoStrategy)
- **Métodos especiais:** `__str__`, `__repr__`, `__eq__`, `__hash__`, `__lt__`, `__iter__`

---

##  Documentação

O projeto utiliza:
- **Type hints** em todo o código
- **Docstrings** no padrão Google
- **Exceções customizadas** para tratamento de erros

## Etiquetas

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
## Autores

- [@Juliett Figueirêdo](https://github.com/juliettfigueiredodev)
- [@Juan Carlos](https://github.com/JuanCostaDev)
- [@Linderval Matias](https://github.com/Linderval-Moura)
- [@Leandro Pereira](https://github.com/leandropereira-alt)




