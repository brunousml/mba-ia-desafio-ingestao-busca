import argparse
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import env, load_env, provider


def _embeddings():
    p = provider()

    if p == "openai":
        from langchain_openai import OpenAIEmbeddings

        api_key = env("OPENAI_API_KEY", prompt="OPENAI_API_KEY", secret=True)
        model = env(
            "OPENAI_EMBEDDING_MODEL",
            prompt="OPENAI_EMBEDDING_MODEL",
            default="text-embedding-3-small",
        )
        return OpenAIEmbeddings(api_key=api_key, model=model)

    if p == "gemini":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        api_key = env("GOOGLE_API_KEY", prompt="GOOGLE_API_KEY", secret=True)
        model = env(
            "GOOGLE_EMBEDDING_MODEL",
            prompt="GOOGLE_EMBEDDING_MODEL",
            default="models/embedding-001",
        )
        return GoogleGenerativeAIEmbeddings(google_api_key=api_key, model=model)

    raise ValueError("Provider invalido. Use PROVIDER=openai ou PROVIDER=gemini.")


def ingest_pdf(*, pdf_path: str, reset: bool) -> None:
    database_url = env("DATABASE_URL", prompt="DATABASE_URL")
    collection_name = env("PG_VECTOR_COLLECTION_NAME", prompt="PG_VECTOR_COLLECTION_NAME")

    pdf_file = Path(pdf_path).expanduser()
    if not pdf_file.exists():
        raise FileNotFoundError(f"PDF_PATH nao encontrado: {pdf_file}")

    loader = PyPDFLoader(str(pdf_file))
    pages = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(pages)

    vectorstore = PGVector(
        embeddings=_embeddings(),
        collection_name=collection_name,
        connection=database_url,
        pre_delete_collection=reset,
    )

    vectorstore.add_documents(chunks)

    print(
        "Ingestao concluida. "
        f"pages={len(pages)} chunks={len(chunks)} collection={collection_name} reset={reset}"
    )


def main() -> None:
    load_env()

    parser = argparse.ArgumentParser(description="Ingestao de PDF para PGVector (Postgres).")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Apaga e recria a colecao antes de inserir (modo desenvolvimento).",
    )
    parser.add_argument(
        "--pdf",
        default=None,
        help="Caminho do PDF. Se omitido, usa PDF_PATH via env (ou solicita em runtime).",
    )
    args = parser.parse_args()

    pdf_path = args.pdf or env("PDF_PATH", prompt="PDF_PATH")
    ingest_pdf(pdf_path=pdf_path, reset=args.reset)


if __name__ == "__main__":
    main()

