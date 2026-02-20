# Desafio MBA Engenharia de Software com IA - Full Cycle

Guia rápido para configuração inicial do ambiente.

## Pré-requisitos

- Python 3.11+
- Docker e Docker Compose

## 1) Configurar variáveis de ambiente

Crie o arquivo `.env` a partir do exemplo:

```bash
cp .env.example .env
```

Preencha os valores obrigatórios no `.env`, principalmente:

- `OPENAI_API_KEY` ou `GOOGLE_API_KEY`
- `DATABASE_URL`
- `PG_VECTOR_COLLECTION_NAME`
- `PDF_PATH`

Exemplo de `DATABASE_URL` local:

```bash
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag
```

## 2) Subir banco com pgvector

```bash
docker compose up -d
```

Esse comando sobe o PostgreSQL e inicializa a extensão `vector`.

## 3) Criar ambiente virtual e instalar dependências

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 4) Próximos passos (execução)

Após configurar o ambiente, execute os scripts da pasta `src` conforme a implementação:

```bash
python src/ingest.py
python src/chat.py
```
