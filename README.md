# Desafio MBA Engenharia de Software com IA - Full Cycle

Implementação do desafio de **ingestão de PDF** + **busca semântica** com **LangChain** e **PostgreSQL + pgvector**.

## Pré-requisitos

- Python 3.11+
- Docker e Docker Compose

## Configurar variáveis de ambiente

Crie o arquivo `.env` a partir do exemplo:

```bash
cp .env.example .env
```

Preencha os valores no `.env` (ou deixe para o script solicitar em runtime), principalmente:

- `OPENAI_API_KEY` (ou `GOOGLE_API_KEY` se usar Gemini)
- `DATABASE_URL`, `PG_VECTOR_COLLECTION_NAME`
- `PDF_PATH`

Exemplo de `.env`:

```bash
PROVIDER=openai
LLM_TEMPERATURE=0

OPENAI_API_KEY=seu_token_aqui
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_LLM_MODEL=gpt-5-nano


GOOGLE_API_KEY=seu_token_aqui
GOOGLE_EMBEDDING_MODEL=gemini-embedding-001
GOOGLE_LLM_MODEL=gemini-2.5-flash-lite

DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag
PG_VECTOR_COLLECTION_NAME=rag_docs

PDF_PATH=./document.pdf
```

Observação: `LLM_TEMPERATURE=0` é recomendado para reduzir risco de respostas fora do CONTEXTO.

# Execução Local via terminal
## Ordem de execução

1) Subir o banco de dados:

```bash
docker compose up -d
```

2) Executar ingestão do PDF:

```bash
python3 src/ingest.py
```

3) Rodar o chat:

```bash
python3 src/chat.py
```

## Execução via Docker Compose (app + banco)

```bash
docker compose -f docker-compose-rag.yml run --rm chat
```

Observação: para execução via Docker, configure `DATABASE_URL_DOCKER` no `.env` (ex.: `postgresql+psycopg://postgres:postgres@postgres:5432/rag`). Dentro do container, `localhost` não aponta para o serviço do banco.
