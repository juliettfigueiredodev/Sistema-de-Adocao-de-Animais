
'''
cobrir regras críticas (políticas, expiração da reserva, cálculo de compatibilidade, transições de estado, estratégias de taxa).
'''
import pytest
from src.infrastructure.settings_loader import SettingsLoader
from src.models.adotante import Adotante
from src.models.animal import Animal
from src.services.compatibilidade_service import CompatibilidadeService


class TestCompatibilidadeService:
    def test_score_100_adotante_ideal():
        '''
        Docstring for test_score_100_adotante_ideal
        Cenário ideal
        Adotante com casa, experiência e sem crianças
        Animal porte G, dócil e calmo
        
        '''
        compatibilidade = CompatibilidadeService()

        adotante1 = Adotante(
            nome='Juliett',
            moradia='casa',
            experiencia=True,
            criancas=False,
            outros_animais=False
        )

        animal1 = Animal(nome='Amora', porte='G', temperamento=['docil', 'calmo'])

        score = compatibilidade.calcular(adotante1, animal1)

        assert score == 100

    def test_penalidade_animal_G_apartamento():
        '''
        Docstring for test_penalidade_animal_G_apartamento
        Cenário em que animal porte G em apto perde 15 pontos de moradia
        Espera-se 85 pontos
        '''
        compatibilidade = CompatibilidadeService()

        adotante2 = Adotante(
            nome='Alice',
            moradia='apartamento',
            experiencia=True,
            criancas=False,
            outros_animais=False
        )

        animal2 = Animal(nome='Alfredo', porte='G', temperamento=['dócil'])

        score = compatibilidade.calcular(adotante2, animal2)

        assert score == 85

    def test_penalidade_animal_arisco_com_crianca():
        '''
        Docstring for test_penalidade_animal_arisco_com_crianca
        Cenário que adotante tem criança e o animal é arisco
        Perde pontos no critério de crianças e de temperamento
        Score < 90
        '''

        compatibilidade = CompatibilidadeService()

        adotante3 = Adotante(
            nome='Clara',
            moradia='casa',
            experiencia=True,
            criancas=True,
            outros_animais=False
        )

        animal3 = Animal(nome='Peralta', porte='P', temperamento=['arisco'])

        score = compatibilidade.calcular(adotante3, animal3)

        assert score < 90