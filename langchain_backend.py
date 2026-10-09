"""LangChain adapter for the original OpenAI-compatible generation backend.

The RAG decision logic, vector index, UI and local model fallback remain unchanged.
LangSmith tracing is controlled externally by LANGSMITH_TRACING=true.
"""
from functools import lru_cache
from urllib.parse import urlsplit, urlunsplit


def _api_root(completions_url: str) -> str:
    """ChatOpenAI expects an API root, not the /chat/completions URL."""
    parsed = urlsplit(completions_url.strip())
    path = parsed.path.rstrip("/")
    suffix = "/chat/completions"
    if not path.endswith(suffix):
        raise ValueError("LLM_BASE_URL must end with /chat/completions")
    return urlunsplit((parsed.scheme, parsed.netloc, path[:-len(suffix)], "", ""))


@lru_cache(maxsize=8)
def _client(base_url: str, api_key: str, model: str, temperature: float, max_tokens: int):
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        base_url=_api_root(base_url), api_key=api_key, model=model,
        temperature=temperature, max_tokens=max_tokens,
        timeout=25, max_retries=1,
    )


def generate(base_url: str, api_key: str, model: str, system_prompt: str,
             user_prompt: str, max_new_tokens: int, temperature: float = 0.3) -> str:
    from langchain_core.messages import HumanMessage, SystemMessage
    llm = _client(base_url, api_key, model, temperature, max_new_tokens)
    response = llm.invoke([
        SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)
    ])
    # The existing code requires a string (not an AIMessage).
    if isinstance(response.content, str):
        return response.content.strip()
    return "".join(part if isinstance(part, str) else part.get("text", "")
                   for part in response.content).strip()
