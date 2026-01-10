
'''

cobrir regras críticas (políticas, expiração da reserva, cálculo de compatibilidade, transições de estado, estratégias de taxa).

'''
import pytest
from src.infrastructure.settings_loader import SettingsLoader
from src.models.adotante import Adotante
from src.models.cachorro import Cachorro
from src.models.gato import Gato
from src.services.compatibilidade_service import CompatibilidadeService


class TestCompatibilidadeService:

    def test_score_100_adotante_ideal(self):
        '''
        Docstring for test_score_100_adotante_ideal
        Cenário ideal
        Adotante com casa, experiência e sem crianças
        Animal porte G, dócil e calmo
        
        '''
        compatibilidade = CompatibilidadeService()
        

        adotante1 = Adotante(
            nome='Juliett',
            idade=28,
            moradia='casa',
            area_util=100,
            experiencia=True,
            criancas=False,
            outros_animais=False
        )

        animal1 = Cachorro(
            raca='Labrador',
            nome='Amora',
            sexo='F',
            idade_meses=24,
            porte='G',
            necessidade_passeio=8,
            temperamento=['docil', 'calmo']
        )

        score = compatibilidade.calcular(adotante1, animal1)

        assert score == 100

    def test_penalidade_animal_G_apartamento(self):
        '''
        Docstring for test_penalidade_animal_G_apartamento
        Cenário em que animal porte G em apto perde 15 pontos de moradia
        Espera-se 85 pontos
        '''
        compatibilidade = CompatibilidadeService()


        adotante2 = Adotante(
            nome='Alice',
            idade=35,
            moradia='apartamento',
            area_util=60,
            experiencia=True,
            criancas=False,
            outros_animais=False
        )

        animal2 = Cachorro(
            raca='Pastor Alemão',
            nome='Alfredo',
            sexo='M',
            idade_meses=24,
            porte='G',
            necessidade_passeio=9,
            temperamento=['docil']
        )

        score = compatibilidade.calcular(adotante2, animal2)

        assert score == 85

    def test_penalidade_animal_arisco_com_crianca(self):
        '''
        Docstring for test_penalidade_animal_arisco_com_crianca
        Cenário que adotante tem criança e o animal é arisco
        Perde pontos no critério de crianças e de temperamento
        Score < 90
        '''

        compatibilidade = CompatibilidadeService()

        

        adotante3 = Adotante(
            nome='Clara',
            idade=32,
            moradia='casa',
            area_util=120,
            experiencia=True,
            criancas=True,
            outros_animais=False
        )

        animal3 = Gato(
            raca='Siamês',
            nome='Peralta',
            sexo='M',
            idade_meses=12,
            porte='P',
            independencia=8,
            temperamento=['arisco']
        )

        score = compatibilidade.calcular(adotante3, animal3)
        
        assert score < 90