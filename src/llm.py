"""
LLM + embeddings provider layer.

Everything that touches an actual model lives here, behind two functions:
  get_chat_model(fast=False)  -> a LangChain chat model, or None in mock mode
  get_embeddings()            -> a LangChain embeddings object, or None in mock mode

Nothing else in the codebase should import langchain_groq / langchain_huggingface
directly - tools and graph nodes call these two functions and branch on
`config.MODE`, which keeps the live/mock split in one place.

Free-tier note: Groq's free developer tier (console.groq.com) needs no
credit card. As of August 2026 their previous default models
(llama-3.1-8b-instant, llama-3.3-70b-versatile) are being retired in favor
of openai/gpt-oss-20b and openai/gpt-oss-120b - see config.py. If Groq's
lineup has changed again by the time you read this, just update
GROQ_MODEL_SMART / GROQ_MODEL_FAST in your .env; nothing else needs to change.
"""

from __future__ import annotations

from functools import lru_cache

from . import config


@lru_cache(maxsize=2)
def get_chat_model(fast: bool = False):
    """Return a ChatGroq instance, or None if we're in mock mode.

    fast=True selects the smaller/faster model (good for cheap classification
    steps like intent routing); fast=False selects the larger model (report
    generation, comparisons - anything where reasoning quality matters more
    than latency).
    """
    if config.MODE != "live":
        return None

    from langchain_groq import ChatGroq

    model_name = config.GROQ_MODEL_FAST if fast else config.GROQ_MODEL_SMART
    return ChatGroq(
        model=model_name,
        temperature=0.2,
        groq_api_key=config.GROQ_API_KEY,
    )


@lru_cache(maxsize=1)
def get_embeddings():
    """Return a local HuggingFace sentence-transformers embedder, or None in mock mode.

    Runs entirely on-device after the first model download (~80MB, cached by
    huggingface_hub) - no per-call API cost, no rate limit, works offline
    after that first run.
    """
    if config.MODE != "live":
        return None

    from langchain_huggingface import HuggingFaceEmbeddings

    return HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)
