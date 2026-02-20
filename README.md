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
- `OPENAI_EMBEDDING_MODEL` (ex: `text-embedding-3-small`)
- `GOOGLE_EMBEDDING_MODEL` (ex: `models/embedding-001`)
- `DATABASE_URL`
- `PG_VECTOR_COLLECTION_NAME`
- `PDF_PATH`
- `PROVIDER` (opcional; `openai` ou `gemini`)
- `LLM_TEMPERATURE` (opcional; default `0`)

Exemplo de `.env` (baseado em `.env.example`):

```bash
# Provider (opcional; se ausente o script pergunta em runtime)
PROVIDER=openai
LLM_TEMPERATURE=0

# OpenAI (opcional se usar Gemini)
OPENAI_API_KEY=seu_token_aqui
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Gemini (opcional se usar OpenAI)
GOOGLE_API_KEY=seu_token_aqui
GOOGLE_EMBEDDING_MODEL=models/embedding-001

# Postgres + pgvector
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag
PG_VECTOR_COLLECTION_NAME=rag_docs

# PDF
PDF_PATH=./document.pdf
```

### Como configurar `LLM_TEMPERATURE` (referências)

`LLM_TEMPERATURE` controla o grau de aleatoriedade/criatividade da LLM. Para este desafio (responder apenas com base no CONTEXTO), valores baixos tendem a ser melhores.

- `0` (recomendado): mais determinístico, menor risco de inventar.
- `0.1` a `0.3`: ainda bem controlado, com pequena variação.
- `0.5` a `0.8`: mais “criativo”, aumenta risco de sair do contexto.
- `1.0+`: alta variabilidade; geralmente não recomendado para RAG restrito.

Exemplos:

```bash
LLM_TEMPERATURE=0
LLM_TEMPERATURE=0.2
```

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
python3 src/ingest.py
python3 src/chat.py
```

## Rodar o chat (CLI)

Após a ingestão, rode o chat:

```bash
python3 src/chat.py
```

Comandos no chat:

- `:help` mostra ajuda
- `:exit` ou `:quit` sai do chat

Opções úteis:

```bash
python3 src/chat.py --debug
python3 src/chat.py --k 10 --max-context-chars 12000
```

## Testar upload (ingestão) de arquivos PDF

O “upload” do desafio é a ingestão do PDF no Postgres + pgvector.

1) Suba o banco:

```bash
docker compose up -d
```

2) Ingerir o PDF padrão do repositório:

```bash
python3 src/ingest.py --pdf ./document.pdf --reset
```

Se alguma variável não estiver no ambiente/.env, o script vai solicitar no terminal em tempo de execução (ex: `DATABASE_URL`, `PG_VECTOR_COLLECTION_NAME`, `OPENAI_API_KEY`/`GOOGLE_API_KEY`).

3) Ingerir outro arquivo PDF:

```bash
python3 src/ingest.py --pdf "/caminho/para/outro-arquivo.pdf"
```

- Para substituir os vetores da coleção, use `--reset`.
- Para manter múltiplos arquivos separados, altere `PG_VECTOR_COLLECTION_NAME` entre execuções.

4) Validar no banco (opcional):

```bash
docker exec -it postgres_rag psql -U postgres -d rag
```

Dentro do `psql`, liste tabelas e verifique registros:

```sql
\dt
-- Em instalações padrão do langchain-postgres, procure por tabelas como:
-- langchain_pg_collection / langchain_pg_embedding
```

## Testar busca (sem LLM) e montagem do prompt

Após ingerir o PDF, você pode testar a recuperação (top-k) e a montagem do prompt (Etapa 3) direto pelo terminal:

```bash
python3 -c "from src.search import search_prompt; run=search_prompt(); prompt,_=run('Qual o faturamento?'); print(prompt[:800])"
```

- Esse teste imprime o início do prompt (com `CONTEXTO` + `REGRAS`).
- Se alguma variável não estiver no ambiente/.env, será solicitada em tempo de execução.
