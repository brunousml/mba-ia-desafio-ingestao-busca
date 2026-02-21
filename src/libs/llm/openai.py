from libs.config import env


def get_embeddings():
    from langchain_openai import OpenAIEmbeddings

    api_key = env("OPENAI_API_KEY", prompt="OPENAI_API_KEY", secret=True)
    model = env(
        "OPENAI_EMBEDDING_MODEL",
        prompt="OPENAI_EMBEDDING_MODEL",
        default="text-embedding-3-small",
    )
    return OpenAIEmbeddings(api_key=api_key, model=model)


def get_llm():
    from langchain_openai import ChatOpenAI

    api_key = env("OPENAI_API_KEY", prompt="OPENAI_API_KEY", secret=True)
    model = env("OPENAI_LLM_MODEL", prompt="OPENAI_LLM_MODEL", default="gpt-5-nano")
    try:
        temperature = float(env("LLM_TEMPERATURE", prompt="LLM_TEMPERATURE", default="0"))
    except ValueError as e:
        raise ValueError("LLM_TEMPERATURE deve ser um numero (ex: 0, 0.2, 1).") from e
    return ChatOpenAI(api_key=api_key, model=model, temperature=temperature)

