# Plano de implementacao do desafio (RAG com PDF + pgvector)

Objetivo: implementar ingestao de um PDF em PostgreSQL+pgvector e uma CLI de perguntas/respostas que responda apenas com
base no conteudo recuperado.

## Decisoes iniciais (antes de codar)

- Provider de embeddings/LLM: escolher 1 caminho primario (OpenAI ou Gemini) e manter o outro como opcional via env.
  - Decisão: 
    - Deve utilizar o provider definido em variável de ambiente
    - Caso as variáveis de ambiente não existam, solicitar em tempo de execução o input do usuário no terminal.  
    - UTILIZE ESTA DEFINIÇÃO PARA TOODAS AS VARIAVEIS DE AMBIENTE.
- Driver Postgres: padronizar em `psycopg` (sincrono) para simplificar; evitar usar multiplos drivers no core.
  - Decisão:
    - Utilize a opção sincrona. 
- Estrategia de RAG: `PGVector` como vector store, `similarity_search_with_score(query, k=10)` para recuperar, e prompt
  fixo conforme especificacao.
  - Decisão:
    - pode seguir com a sugestão.

## Estrutura de codigo (proposta)

Manter os entrypoints exigidos e adicionar modulos internos pequenos:

- `src/ingest.py`: CLI/entrypoint de ingestao
- `src/search.py`: construcao do retriever e prompt/chain
- `src/chat.py`: CLI de interacao (loop de perguntas)
- `src/config.py`: leitura/validacao de variaveis de ambiente
- `src/db.py`: conexao e inicializacao (pgvector/colecao)
- `src/rag.py`: funcoes de chunking, embeddings, ingestao e busca

Se preferir nao criar novos arquivos, o mesmo conteudo pode ficar nos 3 scripts; a modularizacao e so para manter o
projeto evolutivo.

## Etapa 1: configuracao e validacoes basicas

- Garantir `.env` com:
    - `DATABASE_URL`, `PG_VECTOR_COLLECTION_NAME`, `PDF_PATH`
    - `OPENAI_API_KEY` e/ou `GOOGLE_API_KEY`
    - `OPENAI_EMBEDDING_MODEL` (default `text-embedding-3-small`) e/ou `GOOGLE_EMBEDDING_MODEL` (default
      `models/embedding-001`)
    - `OPENAI_LLM_MODEL` (default `gpt-5-nano`) e/ou `GOOGLE_LLM_MODEL` (default `gemini-2.5-flash-lite`)
- `docker compose up -d` sobe Postgres e cria extensao `vector` (ja existe no repo).
- Adicionar checagem no codigo: falhar cedo com mensagem clara se faltar env obrigatoria.

## Etapa 2: ingestao do PDF (src/ingest.py)

Requisitos:

- Carregar PDF via `PyPDFLoader`.
- Split em chunks:
    - `chunk_size=1000`
    - `chunk_overlap=150`
    - usar `RecursiveCharacterTextSplitter`
- Para cada chunk:
    - gerar embedding
    - persistir no `PGVector` usando `collection_name=PG_VECTOR_COLLECTION_NAME`
- Metadados recomendados por chunk:
    - `source` (caminho do PDF)
    - `page` (numero da pagina)
    - `chunk` (indice do chunk na pagina/documento)

Saida/operacao:

- Logar quantidade de paginas, chunks criados e total inserido.
- Ser idempotente no desenvolvimento:
    - opcao A: apagar/recriar colecao (flag `--reset`)
    - opcao B: usar `document_id`/hash para nao duplicar (mais trabalho)

## Etapa 3: busca semantica + montagem de contexto (src/search.py)

Requisitos:

- Dada uma pergunta:
    - vetorizar a pergunta com o mesmo modelo de embeddings usado na ingestao
    - recuperar top 10: `similarity_search_with_score(query, k=10)`
    - concatenar o conteudo (`page_content`) em um `contexto` textual
- Montar o prompt fixo (o do enunciado) com:
    - `contexto` = resultados concatenados
    - `pergunta` = pergunta do usuario

Boas praticas:

- Cortar contexto por tamanho maximo (ex: limite por caracteres) para evitar prompt gigante.
- Incluir separadores entre chunks no contexto (ex: `\n\n---\n\n`).
- Guardar os scores (para debug) e, se necessario, filtrar por threshold (opcional).

## Etapa 4: chamada da LLM com regra "apenas contexto"

Requisitos:

- Chamar uma LLM (OpenAI ou Gemini) com o prompt fixo.
- Responder estritamente baseado no `CONTEXTO`, e se nao houver informacao explicita no contexto, responder exatamente:
    - `Nao tenho informacoes necessarias para responder sua pergunta.`

Implementacao:

- Construir uma chain simples:
    - `prompt_template` + `llm` -> `invoke`
- Evitar "tools", "function calling" e afins no MVP; reduzir superficie de erro.
- Opcional: ajustar temperatura para baixa (ex: 0 a 0.2) para reduzir alucinacao.

## Etapa 5: CLI de chat (src/chat.py)

Requisitos:

- Loop no terminal:
    - imprimir "Faca sua pergunta:"
    - ler input
    - se input vazio: continuar
    - comandos utilitarios:
        - `:exit` / `:quit` para sair
        - `:help` para mostrar comandos
- Para cada pergunta:
    - chamar busca + LLM
    - imprimir:
        - `PERGUNTA: ...`
        - `RESPOSTA: ...`

Opcional (debug):

- Flag `--debug` para exibir fontes:
    - pagina e score dos top-k
    - primeiros N caracteres de cada chunk usado

## Etapa 6: observabilidade e resiliencia

- Mensagens de erro objetivas:
    - falha de conexao Postgres
    - colecao inexistente (ingestao nao feita)
    - erro de leitura do PDF
    - chave da API ausente/invalida
- Timeouts razoaveis para rede (LLM).

## Etapa 7: validacao (manual + automatizada)

Manual:

- Rodar `docker compose up -d`
- Rodar `python src/ingest.py` (deve inserir chunks)
- Rodar `python src/chat.py` e testar:
    - pergunta cuja resposta esta no PDF
    - pergunta fora de contexto (deve retornar a frase padrao)

Automatizada (minimo viavel):

- Criar testes unitarios para:
    - split: garante tamanhos e overlap
    - prompt: garante formatacao e frase de fallback presente
- Se nao houver framework de testes no repo, adicionar `pytest` e 2-3 testes basicos.

## Entregaveis e checklist final

- Scripts funcionais:
    - `python src/ingest.py` ingere o PDF no pgvector
    - `python src/chat.py` responde usando apenas contexto
- README:
    - setup do `.env`
    - subir docker
    - ordem de execucao
- `docs/`:
    - este plano aprovado por voce
