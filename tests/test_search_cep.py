from app.domain.services.cep import Cep

# pytest -S -V
def test_search_cep():

    cep = Cep()
    resp = cep.search_cep("65636570")

    print(resp)

