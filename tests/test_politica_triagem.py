import pytest
from src.infrastructure.settings_loader import SettingsLoader
from src.models.adotante import Adotante
from src.models.cachorro import Cachorro
from src.models.gato import Gato
from src.validators.politica_triagem import PoliticaTriagem
from src.validators.exceptions import PoliticaNaoAtendidaError


class TestPoliticaTriagem:
    
     def test_menor_de_18_com_porte_G(self):
        
         politica = PoliticaTriagem()

         adotante1 = Adotante(
             nome='Juliett',
             idade=10,
             moradia='casa',
             area_util=100,
             experiencia=True,
             criancas=False,
             outros_animais=False
         )


         with pytest.raises(PoliticaNaoAtendidaError) as exc_info:
             politica.validar(adotante1, porte_animal='G')

         assert 'idade_minima' in str(exc_info.value).lower()
         assert 18 in str(exc_info.value)

     def test_moradia_nao_permitida_porte_G(self):

        politica = PoliticaTriagem()

        adotante2 = Adotante(
            nome='Alice',
            idade=35,
            moradia='apartamento',
            area_util=60,
            experiencia=True,
            criancas=False,
            outros_animais=False
        )

        with pytest.raises(PoliticaNaoAtendidaError) as exc_info:
            politica.validar(adotante2, porte_animal='G')

        assert ('area_minima_porte_g' in str(exc_info.value).lower() and 'moradia_permitida_porte_g' in str(exc_info.value).lower())
        
     def test_porte_G_area_util_insuficiente(self):

        politica = PoliticaTriagem()

        adotante2 = Adotante(
            nome='Alice',
            idade=35,
            moradia= 'casa',
            area_util=50,
            experiencia=True,
            criancas=False,
            outros_animais=False
        )

        with pytest.raises(PoliticaNaoAtendidaError) as exc_info:
            politica.validar(adotante2, porte_animal='G')

        assert ('area_minima_porte_g' in str(exc_info.value).lower() and 'moradia_permitida_porte_g' in str(exc_info.value).lower())

        