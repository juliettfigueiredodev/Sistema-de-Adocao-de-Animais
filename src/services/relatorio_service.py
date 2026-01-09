from collections import defaultdict
from datetime import timedelta
from src.services.triagem_service import TriagemService


class RelatorioService:
    """
    Serviço responsável por gerar relatórios do sistema
    relacionados à triagem, compatibilidade e histórico
    de adoções.
    """

    def __init__(self):
        self.triagem = TriagemService()

    def top_animais_adotaveis(self, animais, adotantes, limite=5):
        """
        Retorna os animais com maior média de compatibilidade
        considerando apenas adotantes elegíveis.
        """
        resultados = []

        for animal in animais:
            scores = []

            for adotante in adotantes:
                try:
                    score = self.triagem.avaliar(adotante, animal)
                    scores.append(score)
                except Exception:
                    continue

            if scores:
                media = sum(scores) / len(scores)
                resultados.append((animal, media))

        resultados.sort(key=lambda x: x[1], reverse=True)
        return resultados[:limite]

    def taxa_adocoes_por_especie_porte(self, adocoes):
        """
        Retorna a quantidade de adoções agrupadas por
        espécie e porte do animal.
        """
        resultado = defaultdict(int)

        for adocao in adocoes:
            chave = (adocao.animal.especie, adocao.animal.porte)
            resultado[chave] += 1

        return dict(resultado)

    def tempo_medio_entrada_adocao(self, animais):
        """
        Calcula o tempo médio entre a entrada do animal
        no sistema e sua adoção.
        """
        tempos = []

        for animal in animais:
            if animal.data_adocao:
                delta = animal.data_adocao - animal.data_entrada
                tempos.append(delta)

        if not tempos:
            return timedelta(0)

        return sum(tempos, timedelta(0)) / len(tempos)

    def devolucoes_por_motivo(self, devolucoes):
        """
        Retorna a quantidade de devoluções agrupadas por motivo.
        """
        resultado = defaultdict(int)

        for devolucao in devolucoes:
            resultado[devolucao.motivo] += 1

        return dict(resultado)
