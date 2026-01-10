"""
Serviço de geração de relatórios do sistema de adoção.
"""

from collections import defaultdict, Counter
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional

from src.models.adotante import Adotante
from src.models.animal import Animal
from src.services.triagem_service import TriagemService
from src.validators.exceptions import PoliticaNaoAtendidaError


class RelatorioService:
    """
    Gera relatórios estatísticos do sistema de adoção.
    
    Responsável por calcular métricas como:
    - Top animais mais adotáveis (por compatibilidade)
    - Taxa de adoções por espécie e porte
    - Tempo médio entre entrada e adoção
    - Devoluções agrupadas por motivo
    
    Attributes:
        triagem: Serviço de triagem para calcular compatibilidade.
    
    Example:
        >>> service = RelatorioService()
        >>> top = service.top_animais_adotaveis(animais, adotantes, limite=5)
        >>> for animal, score in top:
        ...     print(f"{animal.nome}: {score:.2f}")
    """
    
    def __init__(self):
        """Inicializa o serviço de relatórios."""
        self.triagem = TriagemService()

    def top_animais_adotaveis(
        self, 
        animais: List[Animal], 
        adotantes: List[Adotante], 
        limite: int = 5
    ) -> List[Tuple[Animal, float]]:
        """
        Retorna os animais com maior média de compatibilidade.
        
        Calcula o score de compatibilidade de cada animal com todos
        os adotantes elegíveis (que passam nas políticas) e retorna
        os animais com maiores médias.
        
        Args:
            animais: Lista de animais a avaliar.
            adotantes: Lista de adotantes cadastrados.
            limite: Número máximo de animais no ranking (padrão: 5).
        
        Returns:
            Lista de tuplas (animal, score_medio) ordenada por score decrescente.
        
        Raises:
            ValueError: Se limite for menor ou igual a zero.
        
        Example:
            >>> animais = repo.list()
            >>> adotantes = [adotante1, adotante2, ...]
            >>> top = service.top_animais_adotaveis(animais, adotantes, 5)
            >>> for animal, score in top:
            ...     print(f"{animal.nome}: {score:.2f}%")
        """
        if limite <= 0:
            raise ValueError(f"Limite deve ser maior que zero: {limite}")
        
        if not animais or not adotantes:
            return []
        
        resultados: List[Tuple[Animal, float]] = []

        for animal in animais:
            scores: List[int] = []

            # Avalia compatibilidade com todos os adotantes
            for adotante in adotantes:
                try:
                    # Se passar nas políticas, calcula score
                    score = self.triagem.avaliar(adotante, animal)
                    scores.append(score)
                    
                except PoliticaNaoAtendidaError:
                    # Adotante não elegível para este animal - ignora
                    continue
                    
                except Exception as e:
                    # Outro erro inesperado - loga e continua
                    print(
                        f"[AVISO] Erro ao avaliar {animal.nome} "
                        f"com {adotante.nome}: {e}"
                    )
                    continue

            # Se teve pelo menos uma avaliação válida, calcula média
            if scores:
                media = sum(scores) / len(scores)
                resultados.append((animal, media))
            else:
                # Nenhum adotante foi elegível para este animal
                print(
                    f"[INFO] Animal {animal.nome} não teve nenhuma "
                    f"avaliação válida (nenhum adotante elegível)"
                )

        # Ordena por score decrescente
        resultados.sort(key=lambda x: x[1], reverse=True)
        
        return resultados[:limite]

    def taxa_adocoes_por_especie_porte(
        self, 
        animais_adotados: List[Animal]
    ) -> Dict[Tuple[str, str], int]:
        """
        Retorna quantidade de adoções agrupadas por espécie e porte.
        
        Args:
            animais_adotados: Lista de animais com status ADOTADO.
        
        Returns:
            Dicionário com chave (espécie, porte) e valor quantidade.
        
        Example:
            >>> adotados = [a for a in animais if a.status == AnimalStatus.ADOTADO]
            >>> resultado = service.taxa_adocoes_por_especie_porte(adotados)
            >>> print(resultado)
            {('Cachorro', 'G'): 15, ('Gato', 'P'): 23, ...}
        """
        if not animais_adotados:
            return {}
        
        resultado = defaultdict(int)

        for animal in animais_adotados:
            try:
                chave = (animal.especie, animal.porte)
                resultado[chave] += 1
            except AttributeError as e:
                print(f"[ERRO] Animal com dados inválidos: {e}")
                continue

        return dict(resultado)

    def tempo_medio_entrada_adocao(
        self, 
        animais: List[Animal]
    ) -> Optional[timedelta]:
        """
        Calcula tempo médio entre entrada do animal e sua adoção.
        
        Extrai a data de adoção do histórico de eventos do animal
        (procura por evento do tipo 'ADOCAO' ou mudança de status
        para ADOTADO).
        
        Args:
            animais: Lista de animais (apenas adotados são considerados).
        
        Returns:
            timedelta com o tempo médio, ou None se não houver dados.
        
        Note:
            Animais sem data de adoção identificável são ignorados.
            Animais com data_adocao < data_entrada são ignorados (dados inválidos).
        
        Example:
            >>> animais = repo.list()
            >>> tempo = service.tempo_medio_entrada_adocao(animais)
            >>> if tempo:
            ...     print(f"Tempo médio: {tempo.days} dias")
        """
        if not animais:
            return None
        
        tempos: List[timedelta] = []

        for animal in animais:
            # Tenta extrair data de adoção do histórico
            data_adocao = self._extrair_data_adocao(animal)
            
            if not data_adocao:
                continue
            
            # Converte data_entrada de ISO string para datetime
            try:
                data_entrada = datetime.fromisoformat(animal.data_entrada)
            except ValueError:
                print(
                    f"[ERRO] Animal {animal.nome} tem data_entrada inválida: "
                    f"{animal.data_entrada}"
                )
                continue
            
            # Calcula diferença
            delta = data_adocao - data_entrada
            
            # Validação de sanidade
            if delta < timedelta(0):
                print(
                    f"[AVISO] Animal {animal.nome} tem data_adocao "
                    f"anterior à data_entrada (dados inconsistentes)"
                )
                continue
            
            tempos.append(delta)

        if not tempos:
            return None

        # Calcula média
        tempo_total = sum(tempos, timedelta(0))
        return tempo_total / len(tempos)

    def _extrair_data_adocao(self, animal: Animal) -> Optional[datetime]:
        """
        Extrai a data de adoção do histórico de eventos.
        
        Procura por:
        1. Evento do tipo 'ADOCAO'
        2. Mudança de status para 'ADOTADO'
        
        Args:
            animal: Animal cujo histórico será analisado.
        
        Returns:
            Data/hora da adoção, ou None se não encontrar.
        """
        for evento in animal:  # Animal implementa __iter__
            # Verifica se é evento de adoção
            if evento.tipo in ("ADOCAO", "MUDANCA_STATUS"):
                # Para MUDANCA_STATUS, verifica se mudou para ADOTADO
                if evento.tipo == "MUDANCA_STATUS":
                    if "ADOTADO" not in evento.detalhes:
                        continue
                
                # Extrai timestamp
                try:
                    data = datetime.fromisoformat(evento.timestamp)
                    return data
                except ValueError:
                    continue
        
        return None

    def devolucoes_por_motivo(
        self, 
        animais: List[Animal]
    ) -> Dict[str, int]:
        """
        Retorna quantidade de devoluções agrupadas por motivo.
        
        Extrai motivos de devolução do histórico de eventos dos animais.
        
        Args:
            animais: Lista de todos os animais (apenas devolvidos são considerados).
        
        Returns:
            Dicionário com motivo como chave e contagem como valor.
        
        Example:
            >>> resultado = service.devolucoes_por_motivo(animais)
            >>> for motivo, qtd in resultado.items():
            ...     print(f"{motivo}: {qtd} devoluções")
        """
        if not animais:
            return {}
        
        motivos: List[str] = []

        for animal in animais:
            # Procura eventos de devolução no histórico
            for evento in animal:
                if evento.tipo in ("DEVOLUCAO", "MUDANCA_STATUS"):
                    # Para MUDANCA_STATUS, verifica se mudou para DEVOLVIDO
                    if evento.tipo == "MUDANCA_STATUS":
                        if "DEVOLVIDO" not in evento.detalhes:
                            continue
                    
                    # Tenta extrair motivo do campo detalhes
                    motivo = self._extrair_motivo(evento.detalhes)
                    if motivo:
                        motivos.append(motivo)

        if not motivos:
            return {}

        return dict(Counter(motivos))

    def _extrair_motivo(self, detalhes: str) -> Optional[str]:
        """
        Extrai o motivo de uma string de detalhes de evento.
        
        Args:
            detalhes: String com detalhes do evento.
        
        Returns:
            Motivo extraído ou None.
        
        Example:
            >>> self._extrair_motivo("Devolvido | motivo: comportamento agressivo")
            'comportamento agressivo'
        """
        # Procura padrão "motivo: XXXX"
        if "motivo:" in detalhes.lower():
            partes = detalhes.split("motivo:")
            if len(partes) >= 2:
                motivo = partes[1].strip()
                # Remove pipes adicionais
                motivo = motivo.split("|")[0].strip()
                return motivo if motivo else None
        
        # Se não encontrou padrão, retorna detalhes completos
        return detalhes.strip() if detalhes.strip() else None

    def __repr__(self) -> str:
        """Representação técnica do serviço."""
        return f"RelatorioService(triagem={self.triagem!r})"
