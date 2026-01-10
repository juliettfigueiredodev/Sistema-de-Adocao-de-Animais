"""
Exceções customizadas do sistema de adoção.
"""


class AdocaoError(Exception):
    """Exceção base para erros do sistema de adoção."""
    pass


class PoliticaNaoAtendidaError(AdocaoError):
    """
    Exceção lançada quando o adotante não cumpre
    alguma política de triagem do sistema.
    
    Example:
        >>> raise PoliticaNaoAtendidaError("Idade mínima não atingida")
    """
    pass


class ReservaInvalidaError(AdocaoError):
    """
    Exceção lançada quando há problemas com reservas.
    
    Example:
        >>> raise ReservaInvalidaError("Animal já está reservado")
    """
    pass


class TransicaoDeEstadoInvalidaError(AdocaoError):
    """
    Exceção lançada quando há tentativa de transição
    inválida de estado do animal.
    
    Example:
        >>> raise TransicaoDeEstadoInvalidaError(
        ...     "Não é possível ir de ADOTADO para DISPONIVEL"
        ... )
    """
    pass


class RepositorioError(AdocaoError):
    """
    Exceção lançada quando há erros no repositório de dados.
    
    Example:
        >>> raise RepositorioError("Erro ao salvar no banco de dados")
    """
    pass


class FilaVaziaError(Exception):    
    pass