from app.core.config import LLM_PROVIDER, CURRENT_MODEL, OPENAI_API_KEY, ANTHROPIC_API_KEY, OLLAMA_BASE_URL

OLLAMA_EMBED_MODEL = "nomic-embed-text"  # dedicated embedding model

def get_llm():
    if LLM_PROVIDER == "ollama":
        from langchain_community.llms import Ollama
        return Ollama(model=CURRENT_MODEL, base_url=OLLAMA_BASE_URL)

    elif LLM_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=CURRENT_MODEL, api_key=OPENAI_API_KEY)

    elif LLM_PROVIDER == "claude":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model=CURRENT_MODEL, api_key=ANTHROPIC_API_KEY)

def get_embeddings():
    if LLM_PROVIDER == "ollama":
        from langchain_community.embeddings import OllamaEmbeddings
        return OllamaEmbeddings(model=OLLAMA_EMBED_MODEL, base_url=OLLAMA_BASE_URL)

    elif LLM_PROVIDER in ("openai", "claude"):
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(api_key=OPENAI_API_KEY)