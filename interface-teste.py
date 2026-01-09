from models.cachorro import Cachorro
from models.gato import Gato
from models.animal_status import AnimalStatus
from infrastructure.animal_repository import AnimalRepository
from services.expiracao_reserva import ExpiracaoReservaJob
from services.reserva_service import ReservaService
from services.adocao_service import AdocaoService
from services.taxa_adocao import TaxaPadrao


def main():
    repo = AnimalRepository("data/animais.json")

    repo.load()
    print("Carregados do JSON:", len(repo.list()))

    dog = Cachorro(
        raca="Vira-lata",
        nome="Rex",
        sexo="M",
        idade_meses=24,
        porte="M",
        necessidade_passeio=7,
        temperamento=["amigável", "brincalhão"],
    )
    cat = Gato(
        raca="Siamês",
        nome="Mia",
        sexo="F",
        idade_meses=12,
        porte="P",
        independencia=9,
        temperamento=["tranquilo"],
    )

    if not any(a.nome == dog.nome and a.especie == dog.especie for a in repo.list()):
        repo.add(dog)
    if not any(a.nome == cat.nome and a.especie == cat.especie for a in repo.list()):
        repo.add(cat)

    repo.save()

    repo2 = AnimalRepository("data/animais.json")
    repo2.load()

    rex = repo2.list(especie="Cachorro")[0]

    # 1) reserva (48h)
    reserva_service = ReservaService(repo2, duracao_horas=48)
    reserva_service.reservar(rex.id, "Fulano")

    # 2) adota
    adocao_service = AdocaoService(repo2)
    contrato = adocao_service.adotar(rex.id, "Fulano", strategy=TaxaPadrao())
    print("\n--- CONTRATO GERADO ---\n")
    print(contrato)

    # 3) roda job (deve dar 0, porque já foi adotado e não está mais reservado)
    job = ExpiracaoReservaJob(repo2)
    qtd = job.executar()
    print("Reservas expiradas:", qtd)


if __name__ == "__main__":
    main()
