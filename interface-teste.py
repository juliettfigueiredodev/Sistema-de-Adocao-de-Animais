# ------------------------------------------------------------
# TESTE DE INTEGRAÇÃO - JUAN
# Testa se triagem, compatibilidade e relatório estão funcionando juntos
# ------------------------------------------------------------

from src.models.adotante import Adotante
from src.services.triagem_service import TriagemService
from src.services.relatorio_service import RelatorioService


# ------------------------------------------------------------
# Criando adotantes de teste
# ------------------------------------------------------------

adotantes = [
    Adotante(
        nome="Maria",
        idade=25,
        moradia="casa",
        area_util=80,
        experiencia=True,
        criancas=False,
        outros_animais=True
    ),
    Adotante(
        nome="João",
        idade=16,  # propositalmente inválido
        moradia="apartamento",
        area_util=50,
        experiencia=False,
        criancas=True,
        outros_animais=False
    )
]


# ------------------------------------------------------------
# Animal fake (simula o model Animal)
# ------------------------------------------------------------

class AnimalFake:
    def __init__(self, nome, porte, temperamento):
        self.nome = nome
        self.porte = porte
        self.temperamento = temperamento


animais = [
    AnimalFake("Rex", "G", ["brincalhao"]),
    AnimalFake("Luna", "P", ["calmo"]),
    AnimalFake("Thor", "G", ["arisco"])
]


# ------------------------------------------------------------
# TESTE 1 — TRIAGEM + COMPATIBILIDADE
# ------------------------------------------------------------

triagem = TriagemService()

print("TESTE DE TRIAGEM E COMPATIBILIDADE:\n")

for animal in animais:
    for adotante in adotantes:
        try:
            score = triagem.avaliar(adotante, animal)
            print(
                f"{adotante.nome} pode adotar {animal.nome} "
                f"(score = {score})"
            )
        except Exception as e:
            print(
                f"{adotante.nome} NÃO pode adotar {animal.nome} → {e}"
            )

print("\n" + "-" * 50 + "\n")


# ------------------------------------------------------------
# TESTE 2 — RELATÓRIO (TOP ANIMAIS MAIS ADOTÁVEIS)
# ------------------------------------------------------------

relatorio = RelatorioService()
top = relatorio.top_animais_adotaveis(animais, adotantes)

print("TOP ANIMAIS MAIS ADOTÁVEIS:")
for animal, media in top:
    print(f"{animal.nome} - média de compatibilidade: {media:.1f}")
