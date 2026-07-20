"""
rag.py

This module implements the Retrieval-Augmented Generation (RAG) pipeline
for the TechStore assistant's knowledge base (return policy, warranty,
shipping, payment, and support FAQs).

Responsibilities:
    - Load the plain-text documents from knowledge_base/.
    - Split each document into paragraph-based chunks.
    - Generate an OpenAI embedding for each chunk.
    - Store chunks + embeddings in a local, persistent Chroma collection.
    - Provide retrieve_relevant_chunks(query), which embeds a question and
      returns the most similar chunk(s) from the collection.

This file is intentionally independent of main.py and tools.py -- it
creates its own small OpenAI client (for embeddings only) rather than
importing one from main.py, to avoid a circular import
(main.py -> tools.py -> rag.py -> main.py would be circular).
"""

import glob
import logging
import os

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(__file__), "knowledge_base")
CHROMA_STORE_PATH = os.path.join(os.path.dirname(__file__), "chroma_store")
COLLECTION_NAME = "techstore_knowledge_base"
EMBEDDING_MODEL = "text-embedding-3-small"

DEFAULT_N_RESULTS = 3

_openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

_chroma_client = chromadb.PersistentClient(
    path=CHROMA_STORE_PATH,
    settings=chromadb.Settings(anonymized_telemetry=False),
)
_collection = _chroma_client.get_or_create_collection(name=COLLECTION_NAME)

def load_documents() -> list[tuple[str, str]]:
    """
    Load every .txt file in knowledge_base/ into memory.

    Returns:
        A list of (filename, full_text) tuples, one per document.
    """
    document_paths = sorted(glob.glob(os.path.join(KNOWLEDGE_BASE_DIR, "*.txt")))
    documents = []

    for path in document_paths:
        filename = os.path.basename(path)
        with open(path, "r", encoding="utf-8") as file:
            documents.append((filename, file.read()))

    logger.info("load_documents: loaded %d document(s)", len(documents))
    return documents

def chunk_text(text: str) -> list[str]:
    """
    Split a document's text into paragraph-based chunks.

    Paragraphs are separated by a blank line. This matches how the
    knowledge base documents are actually written (title/intro paragraph,
    blank line, details paragraph), giving short, topically coherent
    chunks with no extra logic needed.

    Args:
        text: The full text of a document.

    Returns:
        A list of non-empty, whitespace-trimmed paragraph chunks.
    """
    raw_paragraphs = text.split("\n\n")
    return [paragraph.strip() for paragraph in raw_paragraphs if paragraph.strip()]

def embed_text(text: str) -> list[float]:
    """
    Generate an OpenAI embedding vector for a piece of text.

    Args:
        text: The text to embed (a chunk, or a user's query).

    Returns:
        A list of floats representing the embedding vector.
    """
    response = _openai_client.embeddings.create(model=EMBEDDING_MODEL, input=text)
    return response.data[0].embedding

def build_knowledge_base() -> None:
    """
    Populate the Chroma collection from knowledge_base/, if it isn't
    already populated.

    This is idempotent: if the collection already has entries (from a
    previous run), it does nothing, avoiding redundant OpenAI embedding
    calls on every app restart. Each chunk gets a deterministic ID
    ("<filename>_<paragraph_index>") so re-running this after a manual
    reset never creates duplicates.
    """
    existing_count = _collection.count()
    if existing_count > 0:
        logger.info("build_knowledge_base: collection already has %d chunk(s), skipping ingestion", existing_count)
        return

    documents = load_documents()

    chunk_ids: list[str] = []
    chunk_texts: list[str] = []
    chunk_embeddings: list[list[float]] = []
    chunk_metadatas: list[dict] = []

    for filename, full_text in documents:
        paragraphs = chunk_text(full_text)
        for index, paragraph in enumerate(paragraphs):
            chunk_ids.append(f"{filename}_{index}")
            chunk_texts.append(paragraph)
            chunk_embeddings.append(embed_text(paragraph))
            chunk_metadatas.append({"source": filename})

    _collection.add(
        ids=chunk_ids,
        documents=chunk_texts,
        embeddings=chunk_embeddings,
        metadatas=chunk_metadatas,
    )
    logger.info("build_knowledge_base: ingested %d chunk(s) from %d document(s)", len(chunk_ids), len(documents))

MAX_RELEVANT_DISTANCE = 1.3

def retrieve_relevant_chunks(query: str, n_results: int = DEFAULT_N_RESULTS) -> list[dict]:
    """
    Retrieve the most relevant knowledge base chunk(s) for a query,
    filtering out chunks that are too dissimilar to be genuinely
    relevant (see MAX_RELEVANT_DISTANCE).

    Chroma's vector search always returns its n_results nearest
    neighbors, even for a query with no real match in the collection --
    it has no built-in concept of "nothing matched." Without filtering,
    a completely unrelated question (e.g. about scuba gear) would still
    come back with some policy chunk attached, risking the model
    misapplying irrelevant text to answer a question it shouldn't
    answer at all.

    Args:
        query: The user's question (e.g., "What's your return policy?").
        n_results: How many candidate chunks to consider, ranked by
            similarity, before distance filtering is applied.

    Returns:
        A list of dicts, each: {"text": "...", "source": "return_policy.txt"}
        Possibly empty, if no chunk was close enough to be relevant.
    """
    query_embedding = embed_text(query)

    results = _collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
    )

    matched_texts = results["documents"][0]
    matched_metadatas = results["metadatas"][0]
    matched_distances = results["distances"][0]

    relevant_chunks = [
        {"text": text, "source": metadata["source"]}
        for text, metadata, distance in zip(matched_texts, matched_metadatas, matched_distances)
        if distance <= MAX_RELEVANT_DISTANCE
    ]

    logger.info(
        "retrieve_relevant_chunks: query=%r -> %d/%d chunk(s) passed relevance threshold",
        query,
        len(relevant_chunks),
        len(matched_texts),
    )
    return relevant_chunks


def debug_retrieve_with_distances(query: str, n_results: int = DEFAULT_N_RESULTS) -> list[dict]:
    """
    Debugging helper: same as retrieve_relevant_chunks, but returns ALL
    candidates with their raw distance scores, unfiltered. Used to
    calibrate MAX_RELEVANT_DISTANCE against real data -- see
    test_rag.py.

    Returns:
        A list of dicts: {"text": "...", "source": "...", "distance": 0.31}
        sorted by distance (most similar first), unfiltered.
    """
    query_embedding = embed_text(query)

    results = _collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
    )

    return [
        {"text": text, "source": metadata["source"], "distance": distance}
        for text, metadata, distance in zip(
            results["documents"][0], results["metadatas"][0], results["distances"][0]
        )
    ]