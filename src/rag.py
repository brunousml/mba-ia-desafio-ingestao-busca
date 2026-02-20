from langchain_postgres import PGVector

from config import env, provider


def get_embeddings():
    p = provider()

    if p == "openai":
        from llm.openai import get_embeddings as get_openai_embeddings

        return get_openai_embeddings()

    if p == "gemini":
        from llm.gemini import get_embeddings as get_gemini_embeddings

        return get_gemini_embeddings()

    raise ValueError("Provider invalido. Use PROVIDER=openai ou PROVIDER=gemini.")


def get_openai_llm():
    from llm.openai import get_llm as get_openai_llm_impl

    return get_openai_llm_impl()


def get_gemini_llm():
    from llm.gemini import get_llm as get_gemini_llm_impl

    return get_gemini_llm_impl()


def get_llm():
    p = provider()

    if p == "openai":
        return get_openai_llm()
    if p == "gemini":
        return get_gemini_llm()
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
