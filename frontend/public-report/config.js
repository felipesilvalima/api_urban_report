// Configuração de ambiente do frontend público de denúncias.
// Ajuste esses valores conforme o ambiente (local, homologação, produção).

// Endereço base da API.
const API_BASE_URL = "http://localhost:8000";

// Quantidade máxima de denúncias que um mesmo CPF pode registrar por dia.
// Deve ficar em sincronia com MAX_COMPLAINTS_PER_CPF no .env do backend.
const MAX_COMPLAINTS_PER_CPF = 3;
