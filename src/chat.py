import argparse

from config import load_env
from search import answer_question

HELP_TEXT = """\
Comandos:
- :help  Mostra esta ajuda
- :exit  Sai do chat
- :quit  Sai do chat
"""


def main() -> None:
    load_env()

    parser = argparse.ArgumentParser(description="CLI de perguntas e respostas (RAG).")
    parser.add_argument("--k", type=int, default=10, help="Top-k resultados do banco vetorial.")
    parser.add_argument(
        "--max-context-chars",
        type=int,
        default=12_000,
        help="Limite de caracteres do CONTEXTO concatenado.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Mostra metadados de recuperacao (page/score).",
    )
    args = parser.parse_args()

    print("Faça sua pergunta:")

    while True:
        try:
            question = input("\nPERGUNTA: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSaindo.")
            return

        if not question:
            continue

        if question in {":exit", ":quit"}:
            print("Saindo.")
            return

        if question == ":help":
            print(HELP_TEXT)
            continue

        answer, results = answer_question(
            question,
            k=args.k,
            max_context_chars=args.max_context_chars,
        )

        print(f"RESPOSTA: {answer}")

        if args.debug:
            for doc, score in results:
                page = doc.metadata.get("page")
                source = doc.metadata.get("source")
                print(f"- page={page} score={score} source={source}")

if __name__ == "__main__":
    main()
