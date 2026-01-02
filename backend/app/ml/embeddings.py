# backend/app/ml/embeddings.py

from typing import List
from fastapi import HTTPException


DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def _require_sentence_transformers():
    try:
        from sentence_transformers import SentenceTransformer  # noqa: F401
        return True
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail=(
                "Embedding service is not enabled because ML dependencies are missing. "
                "Install with: pip install -r requirements-ml.txt"
            ),
        )


def get_embedding_model(model_name: str = DEFAULT_EMBEDDING_MODEL):
    """
    Lazy-load SentenceTransformer model.
    This keeps backend startup clean if ML deps are not installed.
    """
    _require_sentence_transformers()
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(model_name)


def encode_texts(texts: List[str], model_name: str = DEFAULT_EMBEDDING_MODEL):
    """
    Encode a list of texts into embeddings (numpy array).
    """
    model = get_embedding_model(model_name)
    return model.encode(texts, convert_to_numpy=True)


def get_embedding_dim(model_name: str = DEFAULT_EMBEDDING_MODEL) -> int:
    """
    Return embedding dimension for the configured model.

    IMPORTANT:
    - If ML deps are not installed, we return a safe default for MiniLM (384)
      so the backend can still start and other APIs can run.
    - When ML deps are installed, we compute it from the model.
    """
    try:
        model = get_embedding_model(model_name)
        # SentenceTransformer exposes embedding dimension
        return int(model.get_sentence_embedding_dimension())
    except HTTPException:
        # Default dimension for all-MiniLM-L6-v2
        return 384
