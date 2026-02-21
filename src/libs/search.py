from __future__ import annotations

from typing import Callable

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage

from libs.config import load_env
from libs.rag import get_llm, get_vectorstore


PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
""".lstrip()


OUT_OF_CONTEXT_ANSWER = "Não tenho informações necessárias para responder sua pergunta."


def _concat_context(
    results: list[tuple[Document, float]],
    *,
    max_chars: int,
) -> str:
    parts: list[str] = []
    total = 0

    for doc, score in results:
        header = ""
        page = doc.metadata.get("page")
        if page is not None:
            header = f"[page={page} score={score}]\n"
        else:
            header = f"[score={score}]\n"

        chunk = header + (doc.page_content or "").strip()
        if not chunk:
            continue

        # Add separator between chunks; enforce a soft max by truncating the last chunk.
        sep = "\n\n---\n\n" if parts else ""
        remaining = max_chars - total - len(sep)
        if remaining <= 0:
            break

        if len(chunk) > remaining:
            chunk = chunk[:remaining]

        parts.append(sep + chunk)
        total += len(sep) + len(chunk)

        if total >= max_chars:
            break

    return "".join(parts)


def search_context(
    question: str,
    *,
    k: int = 10,
    max_context_chars: int = 12_000,
) -> tuple[str, list[tuple[Document, float]]]:
    """
    Recupera top-k chunks e devolve:
    - contexto concatenado (texto)
    - lista (Document, score) para debug/telemetria
    """
    vs = get_vectorstore()
    results = vs.similarity_search_with_score(question, k=k)
    contexto = _concat_context(results, max_chars=max_context_chars)
    return contexto, results


def build_prompt(*, contexto: str, pergunta: str) -> str:
    return PROMPT_TEMPLATE.format(contexto=contexto, pergunta=pergunta)


def answer_question(
    question: str,
    *,
    k: int = 10,
    max_context_chars: int = 12_000,
) -> tuple[str, list[tuple[Document, float]]]:
    """
    Recupera contexto e chama a LLM com o prompt fixo.
    Retorna (resposta_texto, resultados_retrieval).
    """
    contexto, results = search_context(question, k=k, max_context_chars=max_context_chars)
    if not contexto.strip():
        return OUT_OF_CONTEXT_ANSWER, results

    prompt = build_prompt(contexto=contexto, pergunta=question)

    llm = get_llm()
    msg = llm.invoke([HumanMessage(content=prompt)])
    content = getattr(msg, "content", "") or ""
    return str(content).strip(), results


def search_prompt(
    *,
    k: int = 10,
    max_context_chars: int = 12_000,
) -> Callable[[str], tuple[str, list[tuple[Document, float]]]]:
    """
    Retorna uma funcao que, dada uma pergunta, monta o prompt com contexto recuperado.
    A chamada da LLM fica para a proxima etapa.
    """
    load_env()

    def _runner(question: str) -> tuple[str, list[tuple[Document, float]]]:
        contexto, results = search_context(
            question,
            k=k,
            max_context_chars=max_context_chars,
        )
        return build_prompt(contexto=contexto, pergunta=question), results

    return _runner


def main() -> None:
    """
    Modo utilitario: executa uma unica pergunta via CLI (nao interativo).
    O modo "chat" do desafio fica em src/chat.py.
    """
    import argparse

    load_env()

    parser = argparse.ArgumentParser(description="Busca semantica + resposta (RAG) para uma pergunta.")
    parser.add_argument("--question", required=True, help="Pergunta do usuario.")
    parser.add_argument("--k", type=int, default=10, help="Top-k resultados do banco vetorial.")
    parser.add_argument(
        "--max-context-chars",
        type=int,
        default=12_000,
        help="Limite de caracteres do CONTEXTO concatenado.",
    )
    args = parser.parse_args()

    answer, _ = answer_question(args.question, k=args.k, max_context_chars=args.max_context_chars)
    print(f"RESPOSTA: {answer}")


if __name__ == "__main__":
    main()

