class TransicaoDeEstadoInvalidaError(Exception):
    """Para quando uma mudança de status não é permitida."""
    pass

class FilaVaziaError(Exception):
    """Tratado ao tentar buscar alguém numa fila vazia."""
    pass