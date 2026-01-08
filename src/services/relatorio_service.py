from src.services.triagem_service import TriagemService


class RelatorioService:
    """
    Serviço responsável por gerar relatórios do sistema
    a partir das regras de triagem e compatibilidade.
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
