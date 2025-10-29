# Lumen
API with JWT authentication for banking transactions using FastAPI

Projeto FastAPI assíncrono para operações bancárias (depósitos/saques) com JWT, Docker e testes assíncronos.

Endpoints principais:
- POST /auth/register
- POST /auth/login
- POST /accounts
- GET /accounts/{id}/statement
- POST /accounts/{id}/transactions

Rodar:
- local: uvicorn app.main:app --reload
- com docker: docker-compose up --build

Docs: /docs (Swagger)
