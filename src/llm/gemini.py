from config import env


def get_embeddings():
    from langchain_google_genai import GoogleGenerativeAIEmbeddings

    api_key = env("GOOGLE_API_KEY", prompt="GOOGLE_API_KEY", secret=True)
    model = env(
        "GOOGLE_EMBEDDING_MODEL",
        prompt="GOOGLE_EMBEDDING_MODEL",
        default="models/embedding-001",
    )
    return GoogleGenerativeAIEmbeddings(google_api_key=api_key, model=model)


def get_llm():
    from langchain_google_genai import ChatGoogleGenerativeAI

    api_key = env("GOOGLE_API_KEY", prompt="GOOGLE_API_KEY", secret=True)
    model = env(
        "GOOGLE_LLM_MODEL",
        prompt="GOOGLE_LLM_MODEL",
        default="gemini-2.5-flash-lite",
    )
    return ChatGoogleGenerativeAI(google_api_key=api_key, model=model, temperature=0)

