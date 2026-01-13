# Sistema de Adoção de Animais

Projeto final da disciplina de POO — UFCA

<img width="421" height="445" alt="image" src="https://github.com/user-attachments/assets/2be25cfc-4065-46d7-9af8-64533db9d809" />




---

##  Sobre o Projeto

Sistema para gerenciar todo o fluxo de adoção de animais, incluindo cadastro, triagem de adotantes, reservas, adoções e relatórios estatísticos.

**Principais funcionalidades:**
- Cadastro de animais (cachorros e gatos) com validações
- Triagem automática de adotantes por políticas configuráveis
- Sistema de reservas com expiração automática
- Cálculo de compatibilidade adotante-animal (score 0-100)
- Geração de contratos de adoção com diferentes estratégias de taxa
- Relatórios estatísticos (top 5 adotáveis, taxa de adoções, tempo médio, devoluções)
- Lista de espera com priorização
- Gestão de devoluções e quarentena

---

##  Como Usar

### Pré-requisitos
```bash
Python 3.10+
pytest
```

### Instalação
```bash
git clone https://github.com/juliettfigueiredodev/Sistema-de-Adocao-de-Animais.git
cd Sistema-de-Adocao-de-Animais
pip install pytest
```

### Executando o Sistema
```bash
python app.py
```

### Rodando os Testes
```bash
# Todos os testes
pytest tests/ -v

# Teste específico
pytest tests/test_politica_triagem.py -v
```
 
---

##  Estrutura do Projeto
```
├── data/                        # Dados persistidos
│   ├── animais.json            # Banco de dados de animais
│   ├── adotantes.json          # Banco de dados de adotantes
│   ├── filas.json              # Filas de espera persistidas
│   └── contratos/              # Contratos de adoção gerados
│
├── logs/                        # Logs do sistema
│   └── sistema.log             # Log de eventos (Observer Pattern)
│
├── src/
│   ├── infrastructure/          # Configurações e persistência
│   │   ├── animal_repository.py     # Repositório de animais
│   │   ├── adotante_repository.py   # Repositório de adotantes
│   │   ├── fila_repository.py       # Repositório de filas
│   │   ├── event_logger.py          # Sistema de logs (Observer)
│   │   └── settings_loader.py       # Carregador de configurações
│   │
│   ├── models/                  # Classes de domínio
│   │   ├── adotante.py         # Modelo do adotante
│   │   ├── animal.py           # Classe base abstrata de animal
│   │   ├── animal_status.py    # Enum de status e validações
│   │   ├── cachorro.py         # Modelo específico de cachorro
│   │   ├── fila_espera.py      # Fila de prioridade (heap)
│   │   ├── gato.py             # Modelo específico de gato
│   │   └── pessoa.py           # Classe base de pessoa
│   │
│   ├── services/                # Lógica de negócio
│   │   ├── adocao_service.py          # Processo de adoção
│   │   ├── compatibilidade_service.py # Cálculo de compatibilidade
│   │   ├── expiracao_reserva.py       # Job de expiração
│   │   ├── gestao_animal_service.py   # Gestão de ciclo de vida
│   │   ├── relatorio_service.py       # Geração de relatórios
│   │   ├── reserva_service.py         # Gestão de reservas
│   │   ├── taxa_adocao.py             # Estratégias de taxa (Strategy)
│   │   └── triagem_service.py         # Triagem e políticas
│   │
│   └── validators/              # Validações e exceções
│       ├── exceptions.py        # Exceções customizadas
│       └── politica_triagem.py  # Políticas de validação
│
├── tests/                       # Testes automatizados
│   ├── interface-teste.py
│   └── ...
│
├── app.py                       # Arquivo principal com CLI
├── settings.json                # Configurações do sistema
├── LICENSE
└── README.md
```

---

##  Configurações

O arquivo `settings.json` contém as políticas do sistema:
```json
{
  "politicas": {
    "idade_minima": 18,
    "area_minima_porte_g": 60,
    "moradia_permitida_porte_g": "casa"
  },
  "reserva": {
    "duracao_horas": 48
  },
  "compatibilidade": {
    "pesos": {
      "porte_moradia": 0.30,
      "experiencia": 0.25,
      "criancas": 0.20,
      "temperamento": 0.15,
      "outros_animais": 0.10
    }
  }
}
```
---

##  Conceitos de POO

- **Herança:** Animal → Cachorro/Gato, Pessoa → Adotante
- **Encapsulamento:** @property com validações
- **Polimorfismo:** Estratégias de taxa intercambiáveis
- **Abstração:** Classes abstratas (Animal, TaxaAdocaoStrategy)
- **Métodos especiais:** `__str__`, `__repr__`, `__eq__`, `__hash__`, `__lt__`, `__iter__`

---

##  Tecnologias Utilizadas

- [Python 3.x](https://www.python.org/) — linguagem utilizada no backend da aplicação
- [Git](https://git-scm.com/) — controle de versão do código-fonte
- [GitHub](https://github.com/) — hospedagem do repositório e colaboração
- [VS Code](https://code.visualstudio.com/) — editor de código
- [Pytest](https://docs.pytest.org/) — framework de testes automatizados

---

##  Equipe

- [@Juliett Figueirêdo](https://github.com/juliettfigueiredodev)
- [@Juan Carlos](https://github.com/JuanCostaDev)
- [@Linderval Matias](https://github.com/Linderval-Moura)
- [@Leandro Pereira](https://github.com/leandropereira-alt)

---

##  Licença

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

---

