# Urban Report — Frontend

Dois frontends estáticos (HTML/CSS/JS puro, sem build) que consomem a API FastAPI deste repositório.

- **`public-report/`** — tela pública para qualquer cidadão registrar uma denúncia (CPF, CEP, categoria, foto, descrição).
- **`admin/`** — tela de login + painel administrativo para listar, filtrar, ver detalhes e alterar o status das denúncias.

No painel de detalhes, o campo "Localização" é um link direto para o Google Maps (`https://www.google.com/maps/search/?api=1&query=lat,lng`) — não há mapa embutido na página. O botão "🔄 Atualizar" recarrega a lista sob demanda (não há polling automático).

## Pré-requisitos

A API precisa estar rodando (`docker compose up`) em `http://localhost:8000`. Se usar outro host/porta, ajuste `API_BASE_URL` em `public-report/config.js` e no topo de `admin/api.js`.

`public-report/config.js` também define `MAX_COMPLAINTS_PER_CPF` (padrão `3`, **por dia**), usado só para exibir o aviso na tela — o limite real é aplicado pelo backend via a variável `MAX_COMPLAINTS_PER_CPF` no `.env`, contando apenas denúncias criadas desde a meia-noite UTC. Mantenha os dois valores sincronizados.

O painel admin exibe a foto de cada denúncia lendo diretamente do bucket público do MinIO (`http://localhost:9000/<bucket>`). O valor padrão em `admin/api.js` (`MINIO_PUBLIC_BASE_URL`) usa o bucket `reports`, que é o definido no `.env` de desenvolvimento — ajuste se o seu `MINIO_BUCKET` for diferente.

## Como rodar

O backend libera CORS apenas para `http://localhost:5173`, `http://localhost:3000` e domínios `lovable.dev` (veja `app/cors/config.py`). Sirva cada app com um servidor estático simples nessas portas:

```bash
# Tela pública de denúncia
cd frontend/public-report && python3 -m http.server 5173
# abra http://localhost:5173

# Painel administrativo
cd frontend/admin && python3 -m http.server 3000
# abra http://localhost:3000
```

(Qualquer servidor estático serve — `npx serve`, extensão Live Server, etc. — desde que a origem esteja na lista de CORS acima.)

## Login administrativo

Não existe endpoint público de cadastro: `POST /api/auth/register` exige um token válido de um usuário já autenticado (e só um admin pode criar outro admin). Ou seja, é preciso já existir um usuário `admin=true` na tabela `users` para conseguir logar no painel. Use o usuário admin já existente no banco, ou insira um manualmente/via um script de seed se estiver subindo o projeto do zero.

Após o login, o token de acesso e o refresh token ficam salvos no `localStorage` do navegador. Em um 401 o app tenta renovar automaticamente via `/api/auth/refresh_token` antes de redirecionar para o login.

## Observações sobre a API (encontradas ao integrar)

- **Bug corrigido:** `ComplaintService.__init__` tinha `self.cep_service = Cep(),` (vírgula sobrando), o que transformava o serviço em uma tupla e quebrava com `AttributeError` **toda criação de denúncia** (`POST /api/complaint/`). Já corrigido em `app/domain/services/complaint_service.py`.
- Vários endpoints (`login`, `refresh_token`, `register`, criar/listar/detalhar/alterar status de denúncia) fazem `return payload, codigo` no estilo Flask, mas o FastAPI **não** interpreta isso como `(corpo, status_code)` — ele serializa a tupla inteira como um array JSON `[payload, codigo]` e sempre responde com o status HTTP padrão (200), mesmo para criações (que deveriam ser 201). O frontend já contorna isso (função `unwrap()` em `app.js`/`api.js`), mas vale corrigir no backend usando `Response(status_code=...)` ou `JSONResponse` se quiser códigos HTTP corretos.
- `GET /api/complaint/` e `GET /api/complaint/{id}` não retornam o endereço (`Address`) da denúncia, apenas `latitude`/`longitude`. O painel admin usa essas coordenadas para gerar o link do Google Maps no painel de detalhes.
- Transições de status válidas: `PENDING → ANALYSING` ou `REJECTED`; `ANALYSING → RESOLVED` ou `REJECTED`; `RESOLVED`/`REJECTED` são estados finais. O painel só mostra as ações permitidas para o status atual.
- **Removido:** o `RateLimiter` (`fastapi_throttle`, controlado por `REQUEST_LIMITER`/`SECONDS_PER_DAY` no `.env`) estava aplicado no nível do `complaint_router`/`minio_router` inteiros, contando junto a criação pública de denúncias **e** as chamadas autenticadas do painel admin (listar, detalhar, alterar status) — o admin acabava levando `429 Too Many Requests` assim que a cota do dia era consumida por qualquer uma das duas coisas. A dependência e o pacote foram removidos de `complaint_routers.py`/`minio_routers.py` (e as variáveis `REQUEST_LIMITER`/`SECONDS_PER_DAY` de `main.py`/`.env`) a pedido do time — hoje não há mais limite de requisições por IP nesses endpoints. O único controle de abuso que resta é o limite diário de denúncias por CPF (`MAX_COMPLAINTS_PER_CPF`, ver acima).
- **Bug corrigido:** `complaints.cpf` tinha uma constraint `UNIQUE` no banco (permitia só 1 denúncia por CPF *para sempre*) e `register_repository`/`save_repository` (em `app/infrastructure/repository/base/repository_base.py`) engoliam qualquer erro de banco num `except:` genérico e retornavam `None` — uma segunda denúncia com o mesmo CPF gerava um `AttributeError` não tratado, que por sua vez virava um 500 sem headers de CORS (o navegador reporta isso como `Failed to fetch`, mascarando o erro real). Corrigido: a constraint única foi removida via migration Alembic (`ed62c1bd1b4e_remove_unique_constraint_from_.py`), o repositório agora deixa o erro propagar normalmente, e o serviço valida quantas denúncias aquele CPF já fez **hoje** (`ComplaintRepository.count_by_cpf_today`, UTC) contra o limite `MAX_COMPLAINTS_PER_CPF`, retornando um erro `409` limpo (`ComplaintConflict`) quando o limite diário é atingido. A contagem reseta à meia-noite UTC.
