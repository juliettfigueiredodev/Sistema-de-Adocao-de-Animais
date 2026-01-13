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
│   ├── animais.json
│   └── contratos/
│
├── src/
│   ├── infrastructure/          # Configurações e persistência
│   │   ├── animal_repository.py
│   │   └── settings_loader.py
│   │
│   ├── models/                  # Classes de domínio
│   │   ├── adotante.py
│   │   ├── animal.py
│   │   ├── animal_status.py
│   │   ├── cachorro.py
│   │   ├── fila_espera.py
│   │   ├── gato.py
│   │   └── pessoa.py
│   │
│   ├── services/                # Lógica de negócio
│   │   ├── adocao_service.py
│   │   ├── compatibilidade_service.py
│   │   ├── expiracao_reserva.py
│   │   ├── gestao_animal_service.py
│   │   ├── relatorio_service.py
│   │   ├── reserva_service.py
│   │   ├── taxa_adocao.py
│   │   └── triagem_service.py
│   │
│   └── validators/              # Validações e exceções
│       ├── exceptions.py
│       └── politica_triagem.py
│
├── tests/                       # Testes automatizados
│   ├── interface-teste.py
│   ├── reserva_animal_status.py
│   ├── test_compatibilidade_service.py
│   ├── test_politica_triagem.py
│   └── test_taxa_adocao.py
│
├── app.py                       # Arquivo principal
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

