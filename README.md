# Lumen — API Bancária (FastAPI, JWT, Docker)

API assíncrona construída com FastAPI para gerenciar contas correntes e transações (depósitos/saques). Inclui autenticação JWT, documentação OpenAPI (Swagger) e testes assíncronos.

Principais funcionalidades
- Registro e login de usuário (JWT)
- Criar conta corrente para usuário autenticado
- Registrar transações: depósito e saque
- Exibir extrato (todas as transações + saldo calculado)
- Validações: valores positivos; checagem de saldo para saques

Tecnologias
- FastAPI
- SQLAlchemy + databases (SQLite por padrão)
- JWT (python-jose)
- Passlib (bcrypt)
- Uvicorn
- Pytest + pytest-asyncio + httpx
- Docker / docker-compose

Pré-requisitos
- Docker e docker-compose (recomendado)
- Ou Python 3.11+ com virtualenv

Variáveis de ambiente (opcionais)
- DATABASE_URL (ex: sqlite:///./lumen.db)
- SECRET_KEY (chave JWT)
- OUTRAS: conforme `docker-compose.yml` ou `.env` que você criar

Execução local (desenvolvimento)
1. Crie e ative um virtualenv
2. Instale dependências:
   pip install -r requirements.txt
3. Rode a aplicação:
   uvicorn app.main:app --reload
4. Acesse a documentação:
   - Swagger UI: http://127.0.0.1:8000/docs
   - ReDoc: http://127.0.0.1:8000/redoc

Execução com Docker
1. Build + run:
   docker-compose up --build
2. A API estará em http://0.0.0.0:8000
3. Docs em http://0.0.0.0:8000/docs

Testes
- Testes locais:
  pytest -q
- Testes via Docker (se existir `docker-compose.test.yml` ou Makefile):
  make test
  ou
  docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit --exit-code-from app

Endpoints principais
- POST /auth/register  — registrar usuário (body: { "username", "password" })
- POST /auth/login     — login (body: { "username", "password" }) => retorna { access_token }
- POST /accounts       — criar conta (Authorization: Bearer <token>, body: { "name" })
- POST /accounts/{id}/transactions — criar transação (Authorization, body: { "type": "deposit"|"withdrawal", "amount": 10.50 })
- GET  /accounts/{id}/statement   — obter extrato (Authorization)

Autenticação (JWT)
- Enviar o token no header:
  Authorization: Bearer <access_token>

Exemplos (curl)
1. Registro
   curl -s -X POST http://localhost:8000/auth/register -H "Content-Type: application/json" \
     -d '{"username":"alice","password":"secret123"}'

2. Login
   curl -s -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" \
     -d '{"username":"alice","password":"secret123"}'

   -> Guarde `access_token` retornado

3. Criar conta
   curl -s -X POST http://localhost:8000/accounts -H "Content-Type: application/json" \
     -H "Authorization: Bearer <TOKEN>" -d '{"name":"Conta Corrente"}'

4. Depositar
   curl -s -X POST http://localhost:8000/accounts/1/transactions \
     -H "Content-Type: application/json" -H "Authorization: Bearer <TOKEN>" \
     -d '{"type":"deposit","amount":100.50}'

5. Sacar (validação de saldo)
   curl -s -X POST http://localhost:8000/accounts/1/transactions \
     -H "Content-Type: application/json" -H "Authorization: Bearer <TOKEN>" \
     -d '{"type":"withdrawal","amount":50.25}'

6. Extrato
   curl -s -X GET http://localhost:8000/accounts/1/statement -H "Authorization: Bearer <TOKEN>"

Boas práticas
- Mantenha SECRET_KEY segura (não hardcode em produção).
- Para ambiente de produção, use um banco real (Postgres) e configure DATABASE_URL.
- Habilite HTTPS e proximidade de deployment (Gunicorn/Uvicorn workers, configuração de logs).

Contribuição
- Abra issues ou PRs com melhorias, correções e testes.

Licença
- MIT (ou ajuste conforme necessário).
