from langchain_postgres import PGVector

from config import env, provider


def get_embeddings():
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


def get_vectorstore(*, pre_delete_collection: bool = False) -> PGVector:
    database_url = env("DATABASE_URL", prompt="DATABASE_URL")
    collection_name = env("PG_VECTOR_COLLECTION_NAME", prompt="PG_VECTOR_COLLECTION_NAME")

    return PGVector(
        embeddings=get_embeddings(),
        collection_name=collection_name,
        connection=database_url,
        pre_delete_collection=pre_delete_collection,
    )

