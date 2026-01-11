'''
    Docstring for TestValidarTransicao
    
    Adicionei docstrings apenas aquelas funções que julgo necessitarem de uma explicação melhor do que o próprio nome da função

    Testes de transição de estado dos animais: DISPONIVEL, RESERVADO, ADOTADO, DEVOLVIDO, QUARENTENA, INADOTAVEL
    
    '''
import pytest
from src.models.animal_status import (
    AnimalStatus,
    TransicaoDeEstadoInvalidaError,
    validar_transicao,
)

class TestValidarTransicao:
    
    def test_transicao_valida_disponivel_para_reservado(self):
        """
        Entra no except se houver algum erro na constante TRANSICOES_PERMITIDAS
        Exemplo: Não ter colocado RESERVADO no frozenset de AnimalStatus.DISPONIVEL
        
        """
        try:
            validar_transicao(AnimalStatus.DISPONIVEL, AnimalStatus.RESERVADO)
        except TransicaoDeEstadoInvalidaError:
            pytest.fail('Transição válida  DISPONIVEL -> RESERVADO foi rejeitada')
    
    def test_transicao_valida_reservado_para_adotado(self):
        '''
        Entra no except se houver algum erro na constante TRANSICOES_PERMITIDAS
        Exemplo: Não ter colocado ADOTADO no frozenset de AnimalStatus.RESERVADO
        
        '''
        try:
            validar_transicao(AnimalStatus.RESERVADO, AnimalStatus.ADOTADO)
        except TransicaoDeEstadoInvalidaError:
            pytest.fail('Transição válida RESERVADO -> ADOTADO foi rejeitada')
    
    def test_transicao_invalida_disponivel_para_adotado(self):

        """Não deve permitir pular de DISPONIVEL direto para ADOTADO."""
        try:
            validar_transicao(AnimalStatus.DISPONIVEL, AnimalStatus.ADOTADO)
        except TransicaoDeEstadoInvalidaError: 
            pytest.fail('Transição inválida. Não é permitido sair do status DISPONIVEL direto para ADOTADO, precisa ser RESERVADO antes!')
                
    def test_transicao_invalida_adotado_para_disponivel(self):

        """ Não deve permitir voltar de ADOTADO para DISPONIVEL, pois precisa ir para DEVOLVIDO antes."""
        try:
            validar_transicao(AnimalStatus.ADOTADO, AnimalStatus.DISPONIVEL)
        except TransicaoDeEstadoInvalidaError:
            pytest.fail('Transição inválida! Se ADOTADO não pode seguir para DISPONIVEL')
                
    def test_transicao_invalida_inadotavel_para_qualquer_status(self):
        
        """Animal inadotável não muda de status."""
        try:
            validar_transicao(AnimalStatus.INADOTAVEL, AnimalStatus.DISPONIVEL)
        except TransicaoDeEstadoInvalidaError:
            pytest.fail('Transição inválida! Infelizmente, INADOTAVEL não pode trocar para outro status')
                
    def test_transicao_valida_devolvido_para_disponivel(self):
        
        try:
            validar_transicao(AnimalStatus.DEVOLVIDO, AnimalStatus.DISPONIVEL)
        except TransicaoDeEstadoInvalidaError:
            pytest.fail('Transição válida (DEVOLVIDO -> DISPONIVEL) foi rejeitada')
    
    def test_transicao_invalida_reservado_para_devolvido(self):
        
        """Animal reservado não pode ir direto para devolvido"""
        try:
            validar_transicao(AnimalStatus.RESERVADO, AnimalStatus.DEVOLVIDO)
        except TransicaoDeEstadoInvalidaError:
            pytest.fail('Transição inválida! RESERVADO vai para ADOTADO ou se cancelamento, vai para DISPONIVEL')
            
class TestFluxosCompletos:
    """ Fluxos completos de adoção """
    
    def test_fluxo_adocao_sucesso(self):
        
        validar_transicao(AnimalStatus.DISPONIVEL, AnimalStatus.RESERVADO)
        validar_transicao(AnimalStatus.RESERVADO, AnimalStatus.ADOTADO)
    
    def test_fluxo_reserva_cancelada(self):

        validar_transicao(AnimalStatus.DISPONIVEL, AnimalStatus.RESERVADO)
        validar_transicao(AnimalStatus.RESERVADO, AnimalStatus.DISPONIVEL)
    
    def test_fluxo_devolucao_com_quarentena(self):

        validar_transicao(AnimalStatus.ADOTADO, AnimalStatus.DEVOLVIDO)
        validar_transicao(AnimalStatus.DEVOLVIDO, AnimalStatus.QUARENTENA)
        validar_transicao(AnimalStatus.QUARENTENA, AnimalStatus.DISPONIVEL)
    
    def test_fluxo_devolucao_direta(self):

        """ Devolução sem quarentena: ADOTADO -> DEVOLVIDO -> DISPONIVEL."""

        validar_transicao(AnimalStatus.ADOTADO, AnimalStatus.DEVOLVIDO)
        validar_transicao(AnimalStatus.DEVOLVIDO, AnimalStatus.DISPONIVEL)
    
    def test_animal_vira_inadotavel_depois_devolucao(self):

        """Animal devolvido pode se tornar inadotável."""

        validar_transicao(AnimalStatus.DEVOLVIDO, AnimalStatus.INADOTAVEL)


class TestCasosEspeciais:
    
    def test_mudar_para_mesmo_status(self):

        """Não permite "transição" para o mesmo status."""

        try:
            validar_transicao(AnimalStatus.DISPONIVEL, AnimalStatus.DISPONIVEL)
        except TransicaoDeEstadoInvalidaError:
            pytest.fail('Transição DISPONIVEL -> DISPONIVEL não é permitida!')
            
    
    def test_quarentena_nao_pode_ir_para_adotado(self):

        """Animal em quarentena não pode ser adotado diretamente."""

        try:
            validar_transicao(AnimalStatus.QUARENTENA, AnimalStatus.ADOTADO)
        except TransicaoDeEstadoInvalidaError:
            pytest.fail('Transição de QUARENTENA para ADOTADO não é permitida!')
    
    def test_inadotavel_nao_muda_de_status(self):
        
        """Verifica que inadotável não pode ir para nenhum outro status."""

        todos_status = [
            AnimalStatus.DISPONIVEL,
            AnimalStatus.RESERVADO,
            AnimalStatus.ADOTADO,
            AnimalStatus.DEVOLVIDO,
            AnimalStatus.QUARENTENA,
        ]
        
        for status in todos_status:
            try:
                validar_transicao(AnimalStatus.INADOTAVEL, status)
            except TransicaoDeEstadoInvalidaError:
                pytest.fail('Transição INADOTAVEL para qualquer outro status não é permitido!')