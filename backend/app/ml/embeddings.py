# app/ml/embeddings.py

from functools import lru_cache
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import get_settings
settings = get_settings

@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """
    Load a shared sentence embedding model once per process.

    This model is the SAME across all organizations, which is how we get
    cross-organizational semantic alignment (RQ2).
    """
    model_name = getattr(
        settings,
        "EMBEDDING_MODEL_NAME",
        "sentence-transformers/all-MiniLM-L6-v2",
    )
    return SentenceTransformer(model_name)


def get_embedding_dim() -> int:
    return get_embedding_model().get_sentence_embedding_dimension()


def encode_texts(texts: List[str]) -> np.ndarray:
    """
    Encode a list of texts into normalized embeddings.

    Shape: (len(texts), embedding_dim)
    """
    model = get_embedding_model()
    emb = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,  # cosine geometry
    )
    return emb
