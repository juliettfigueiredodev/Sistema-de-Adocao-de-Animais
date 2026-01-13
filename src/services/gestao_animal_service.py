"""
Serviço de gestão do ciclo de vida dos animais.
"""

from src.models.animal import Animal
from src.models.animal_status import AnimalStatus
from src.models.fila_espera import FilaEspera
from src.validators.exceptions import TransicaoDeEstadoInvalidaError, FilaVaziaError

class GestaoAnimalService:
    """
    Gerencia transições de estado complexas e regras de negócio pós-adoção.
    
    Responsável por processar devoluções, gerenciar quarentena
    e verificar expiração de reservas, garantindo a integridade
    das transições de estado do animal.
    
    Example:
        >>> service = GestaoAnimalService()
        >>> try:
        ...     service.processar_devolucao(animal, "Motivo pessoal", False)
        ... except TransicaoDeEstadoInvalidaError as e:
        ...     print(f"Erro: {e}")
    """

    def processar_devolucao(self, animal: Animal, motivo: str, problema_saude_comportamento: bool) -> None:
        """
        Processa a devolução de um animal adotado.
        
        Realiza a transição de status apropriada:
        - SEM problema: ADOTADO → DEVOLVIDO → DISPONIVEL
        - COM problema: ADOTADO → DEVOLVIDO → QUARENTENA
        
        Args:
            animal: O animal sendo devolvido.
            motivo: A razão informada para a devolução.
            problema_saude_comportamento: Flag indicando se há problemas que
                exijam isolamento (quarentena).
        
        Raises:
            TransicaoDeEstadoInvalidaError: Se o animal não estiver com status ADOTADO.
            Exception: Para erros críticos durante a mudança de status.
        """
        if animal.status != AnimalStatus.ADOTADO:
            raise TransicaoDeEstadoInvalidaError(f"Não é possível devolver um animal com status {animal.status}")

        print(f"--- Processando Devolução de {animal.nome} ---")
        print(f"Motivo registrado: {motivo}")

        # Lógica de decisão de status
        try:
            # Todo animal devolvido vira 'DEVOLVIDO' primeiro
            # Isso satisfaz a regra estrita de transição (ADOTADO -> DEVOLVIDO)
            animal.mudar_status(AnimalStatus.DEVOLVIDO, motivo)
            print(f"Status inicial ajustado para: {AnimalStatus.DEVOLVIDO.value}")

            # Se tiver problema, move de DEVOLVIDO para QUARENTENA
            if problema_saude_comportamento:
                print("Detectado problema de saúde/comportamento. Movendo para Quarentena...")
                animal.mudar_status(
                    AnimalStatus.QUARENTENA, 
                    "Encaminhado automaticamente pós-devolução devido a problemas de saúde/comportamento"
                )
                print(f"ALERTA: Animal movido para {animal.status.value}.")
            else:
                # SEM problema: volta para DISPONIVEL
                print("Sem problemas detectados. Retornando para disponibilidade...")
                animal.mudar_status(
                    AnimalStatus.DISPONIVEL,
                    "Animal devolvido sem problemas - apto para nova adoção"
                )
                print(f"✅ Animal está {animal.status.value} para nova adoção.")

        except Exception as e:
            print(f"Erro crítico ao mudar status: {e}")
            raise e


    def reavaliar_quarentena(self, animal: Animal, apto_adocao: bool) -> None:
        """
        Reavalia um animal que está em quarentena ou devolvido.
        
        Dependendo da avaliação clínica/comportamental, define se o
        animal volta a estar disponível ou se torna inadotável.
        
        Args:
            animal: O animal a ser reavaliado.
            apto_adocao: True se o animal estiver saudável e apto, False caso contrário.
            
        Raises:
            TransicaoDeEstadoInvalidaError: Se o animal não estiver em 
                QUARENTENA ou DEVOLVIDO.
        """
        status_permitidos = [AnimalStatus.QUARENTENA, AnimalStatus.DEVOLVIDO]
        
        if animal.status not in status_permitidos:
            raise TransicaoDeEstadoInvalidaError(f"Apenas animais em Quarentena ou Devolvidos podem ser reavaliados. Status atual: {animal.status}")

        print(f"--- Reavaliando {animal.nome} ---")
        
        if apto_adocao:
            novo_status = AnimalStatus.DISPONIVEL
            resultado = "Aprovado"
        else:
            novo_status = AnimalStatus.INADOTAVEL
            resultado = "Reprovado"

        animal.mudar_status(novo_status, f"Reavaliação: {resultado}")

        print(f"Resultado da reavaliação: {resultado}. Novo status: {novo_status.value}")


    def verificar_expiracao_reserva(self, animal: Animal, fila_espera: FilaEspera) -> None:
        """
        Verifica a expiração de reserva e gerencia a fila de espera.
        
        Se a reserva expirou, notifica o próximo adotante da fila (se houver)
        ou devolve o animal para o status DISPONIVEL.
        
        Args:
            animal: O animal cuja reserva está sendo verificada.
            fila_espera: A fila de espera associada a este animal (ou global).
        """
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
            animal.mudar_status(AnimalStatus.DISPONIVEL, "Expiração de reserva sem fila")
            print(f"Ninguém na fila de espera. {animal.nome} voltou para status DISPONIVEL.")