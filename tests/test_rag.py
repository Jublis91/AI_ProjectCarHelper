import numpy as np
import pytest

from backend import rag


def test_chunk_text_removes_empty_lines_and_chunks():
    text = """
    first line\n\n
      second line   \n\n\n
    """
    chunks = rag.chunk_text(text, chunk_size=50, overlap=10)

    assert chunks == ["first line\nsecond line"]


def test_chunk_text_returns_empty_for_whitespace_only():
    assert rag.chunk_text("   \n\n   ") == []


def test_chunk_text_applies_overlap():
    chunks = rag.chunk_text("abcde", chunk_size=3, overlap=1)
    assert chunks == ["abc", "cde"]


def test_cosine_top_k_basic_ordering():
    query = np.array([1.0, 0.0])
    matrix = np.array([
        [1.0, 0.0],
        [0.0, 1.0],
        [-1.0, 0.0],
    ])

    idx, scores = rag.cosine_top_k(query, matrix, k=2)

    assert idx.tolist() == [0, 1]
    assert scores[0] >= scores[1]


def test_cosine_top_k_handles_empty_matrix():
    idx, scores = rag.cosine_top_k(np.array([1.0, 0.0]), np.array([]), k=3)

    assert idx.size == 0
    assert scores.size == 0


def test_cosine_top_k_validates_dimensions():
    with pytest.raises(ValueError):
        rag.cosine_top_k(np.array([[1.0, 0.0]]), np.array([[1.0, 0.0]]))

    with pytest.raises(ValueError):
        rag.cosine_top_k(np.array([1.0, 0.0]), np.array([1.0, 0.0]))

    with pytest.raises(ValueError):
        rag.cosine_top_k(np.array([1.0, 0.0]), np.array([[1.0, 0.0, 2.0]]))
