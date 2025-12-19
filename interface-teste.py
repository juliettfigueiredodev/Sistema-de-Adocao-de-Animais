#------------------------------------------------------------#
#teste juan
from src.models.adotante import Adotante


adotante = Adotante(
    nome="Maria",
    idade=25,
    moradia="casa",
    area_util=80,
    experiencia=True,
    criancas=False,
    outros_animais=True
)



print(adotante.nome)
print(adotante.idade)
print(adotante.moradia)
print(adotante.area_util)
print(adotante.experiencia)
print(adotante.criancas)
print(adotante.outros_animais)

#------------------------------------------------------------#