from app.domain.services.cep import Cep
from app.domain.services.cpf import Cpf

# pytest -S -V
def test_search_cep():

    cep = Cep()
    resp = cep.search_cep("65636570")

    print(resp)



# def test_search_cpf():

#     cpf = Cpf()
#     resp = cpf.search_cpf("12345678909")

#     print(resp)

