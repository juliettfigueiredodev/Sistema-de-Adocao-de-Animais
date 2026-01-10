from datetime import datetime
from src.models.animal_status import AnimalStatus
from src.validators.exceptions import TransicaoDeEstadoInvalidaError, FilaVaziaError

class GestaoAnimalService:
    
    def processar_devolucao(self, animal, motivo: str, problema_saude_comportamento: bool):
        """
        Devolução registra motivo e ajusta status para DEVOLVIDO ou QUARENTENA.
        """
        if animal.status != AnimalStatus.ADOTADO:
            raise TransicaoDeEstadoInvalidaError(f"Não é possível devolver um animal com status {animal.status}")

        print(f"--- Processando Devolução de {animal.nome} ---")
        print(f"Motivo registrado: {motivo}")

        # Lógica de decisão de status
        if problema_saude_comportamento:
            animal.status = AnimalStatus.QUARENTENA
            print(f"ALERTA: Animal movido para {animal.status.value} devido a problemas de saúde/comportamento.")
        else:
            animal.status = AnimalStatus.DEVOLVIDO
            print(f"Animal movido para status: {animal.status.value}.")
        
        # Registrar no histórico (conforme requisito [cite: 13])
        evento = {
            "data": datetime.now(),
            "evento": "DEVOLUCAO",
            "motivo": motivo,
            "novo_status": animal.status.value
        }
        animal.historico.append(evento)


    def reavaliar_quarentena(self, animal, apto_adocao: bool):
        """
        Reavaliação pode migrar status para DISPONIVEL ou INADOTAVEL.
        """
        status_permitidos = [AnimalStatus.QUARENTENA, AnimalStatus.DEVOLVIDO]
        
        if animal.status not in status_permitidos:
            raise TransicaoDeEstadoInvalidaError(f"Apenas animais em Quarentena ou Devolvidos podem ser reavaliados. Status atual: {animal.status}")

        print(f"--- Reavaliando {animal.nome} ---")
        
        if apto_adocao:
            animal.status = AnimalStatus.DISPONIVEL
            resultado = "Aprovado"
        else:
            animal.status = AnimalStatus.INADOTAVEL
            resultado = "Reprovado"

        print(f"Resultado da reavaliação: {resultado}. Novo status: {animal.status.value}")

        evento = {
            "data": datetime.now(),
            "evento": "REAVALIACAO",
            "resultado": resultado,
            "novo_status": animal.status.value
        }
        animal.historico.append(evento)


    def verificar_expiracao_reserva(self, animal, fila_espera):
        """
        Ao expirar reserva, notificar próximo da fila.
        """
        # Simulação: assumimos que a verificação de tempo já ocorreu e a reserva expirou
        if animal.status != AnimalStatus.RESERVADO:
            print("Este animal não está reservado.")
            return

        print(f"--- Reserva de {animal.nome} Expirou ---")
        
        # Tenta chamar o próximo da fila
        try:
            proximo_adotante = fila_espera.proximo()
            print(f"NOTIFICAÇÃO ENVIADA: Olá {proximo_adotante.nome}, o animal {animal.nome} está disponível para você!")
            
            # Atualiza status (Mantém reservado, mas agora para a nova pessoa)
            print(f"Nova reserva iniciada para {proximo_adotante.nome}.")
            
        except FilaVaziaError:
            # Se não tem ninguém na fila, volta a ficar disponível geral
            animal.status = AnimalStatus.DISPONIVEL
            print(f"Ninguém na fila de espera. {animal.nome} voltou para status DISPONIVEL.")

        evento = {
            "data": datetime.now(),
            "evento": "EXPIRACAO_RESERVA",
            "novo_status": animal.status.value
        }
        animal.historico.append(evento)