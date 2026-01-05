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

    # 1) carregar o que já existe
    repo.load()
    print("Carregados do JSON:", len(repo.list()))

    # 2) cadastrar dois animais
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

    ja_tem_dog = any(a.nome == dog.nome and a.especie == dog.especie for a in repo.list())
    ja_tem_cat = any(a.nome == cat.nome and a.especie == cat.especie for a in repo.list())

    if not ja_tem_dog:
        repo.add(dog)
    if not ja_tem_cat:
        repo.add(cat)



    # 3) listar por status
    disponiveis = repo.list(status=AnimalStatus.DISPONIVEL)
    print("\nDisponíveis:")
    for a in disponiveis:
        print(" -", a)

    # 4) salvar
    repo.save()
    print("\nSalvo no JSON!")

    # 5) testar reload
    repo2 = AnimalRepository("data/animais.json")
    repo2.load()
    print("\nRecarregado:", len(repo2.list()))
    print("Somente gatos:", [a.nome for a in repo2.list(especie="Gato")])

    # 6) reserva
    reserva_service = ReservaService(repo2, duracao_horas=48)
    rex = repo2.list(especie="Cachorro")[0]
    reserva_service.reservar(rex.id, "Fulano")
    
    # 7) adoção efetiva (gera contrato)
    adocao_service = AdocaoService(repo2)
    contrato = adocao_service.adotar(rex.id, "Fulano", strategy=TaxaPadrao())
    print("\n--- CONTRATO GERADO ---\n")
    print(contrato)


    # 8) rodar job de expiração de reserva
    job = ExpiracaoReservaJob(repo2)
    qtd = job.executar()
    print("Reservas expiradas:", qtd)



if __name__ == "__main__":
    main()




