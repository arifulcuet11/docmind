from app.core.config import (
    LLM_PROVIDER,
    CURRENT_MODEL,
    OPENAI_API_KEY,
    ANTHROPIC_API_KEY,
    OLLAMA_BASE_URL,
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL
)

OLLAMA_EMBED_MODEL = "nomic-embed-text"  # dedicated embedding model

def get_llm():
    if LLM_PROVIDER == "ollama":
        from langchain_community.llms import Ollama
        return Ollama(
            model=CURRENT_MODEL,
            base_url=OLLAMA_BASE_URL
        )

    elif LLM_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=CURRENT_MODEL,
            api_key=OPENAI_API_KEY
        )

    elif LLM_PROVIDER == "claude":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=CURRENT_MODEL,
            api_key=ANTHROPIC_API_KEY
        )

    elif LLM_PROVIDER == "openrouter":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=CURRENT_MODEL,
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
            default_headers={
                "HTTP-Referer": "http://localhost",
                "X-Title": "LLM-DOCMIND-APP",
            }
        )

    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}")

def get_embeddings():
    if LLM_PROVIDER == "ollama":
        from langchain_community.embeddings import OllamaEmbeddings
        return OllamaEmbeddings(
            model=OLLAMA_EMBED_MODEL,
            base_url=OLLAMA_BASE_URL
        )

    elif LLM_PROVIDER == "openai":
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=OPENAI_API_KEY
        )

    elif LLM_PROVIDER == "openrouter":
        # OpenRouter does not expose an embeddings endpoint — use OpenAI directly
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=OPENAI_API_KEY,
        )

    elif LLM_PROVIDER == "claude":
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=OPENAI_API_KEY
        )

    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}")