import os
from getpass import getpass

from dotenv import load_dotenv


def load_env() -> None:
    # Load .env if present; runtime prompts fill any missing values.
    load_dotenv()


def _has_env(var_name: str) -> bool:
    value = os.getenv(var_name)
    return value is not None and value.strip() != ""


def _prompt_value(var_name: str, prompt: str, *, default: str | None, secret: bool) -> str:
    while True:
        suffix = f" [{default}]" if default is not None else ""
        message = f"{prompt}{suffix}: "
        value = (getpass(message) if secret else input(message)).strip()
        if not value and default is not None:
            return default
        if value:
            return value
        print(f"Valor obrigatorio ausente: {var_name}.")


def env(
    var_name: str,
    *,
    prompt: str | None = None,
    default: str | None = None,
    secret: bool = False,
) -> str:
    """
    Regra do projeto: toda variavel de ambiente usada pelo codigo deve vir do ambiente.
    Se nao existir, solicitar input do usuario em tempo de execucao no terminal.
    """
    value = os.getenv(var_name)
    if value is not None and value.strip() != "":
        return value

    prompt_text = prompt or f"Informe {var_name}"
    value = _prompt_value(var_name, prompt_text, default=default, secret=secret)
    os.environ[var_name] = value
    return value


def provider() -> str:
    """
    Regra:
    - Se apenas uma API key estiver configurada no ambiente, escolher o provider correspondente sem perguntar.
    - Se as duas API keys estiverem configuradas, usar PROVIDER (env) ou solicitar em runtime.
    - Se nenhuma API key estiver configurada, nao perguntar provider; default para openai (e o codigo vai solicitar a key necessaria).
    """
    has_openai = _has_env("OPENAI_API_KEY")
    has_gemini = _has_env("GOOGLE_API_KEY")

    if has_openai and not has_gemini:
        return "openai"
    if has_gemini and not has_openai:
        return "gemini"

    if has_openai and has_gemini:
        value = env(
            "PROVIDER",
            prompt="Provider (openai ou gemini)",
            default="openai",
            secret=False,
        ).lower()
        if value not in {"openai", "gemini"}:
            raise ValueError("PROVIDER deve ser 'openai' ou 'gemini'.")
        return value

    return "openai"

