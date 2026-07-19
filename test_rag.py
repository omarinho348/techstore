"""
test_rag.py

Standalone script to verify the RAG pipeline works end-to-end: builds
the knowledge base (embeds + stores all chunks, first run only), then
runs a few test retrievals to confirm sensible chunks come back.

Run this directly:

    python test_rag.py

Delete this file once you've confirmed retrieval quality looks good --
it's a debugging tool, not part of the final application.
"""

from rag import build_knowledge_base, debug_retrieve_with_distances

if __name__ == "__main__":
    print("Building knowledge base (this embeds all chunks on first run only)...")
    build_knowledge_base()
    print("Done.\n")

    test_queries = [
        "What's your return policy?",
        "Is water damage covered under warranty?",
        "How long does shipping take?",
        "Can I change my shipping address after placing an order?",
        "What are your store hours?",
        "Where are your physical stores located?",
        "This question shouldn't match anything relevant, like a request about scuba diving gear.",
    ]

    for query in test_queries:
        print(f"Query: {query}")
        results = debug_retrieve_with_distances(query, n_results=2)
        for i, result in enumerate(results):
            print(f"  [{i}] distance={result['distance']:.4f}  ({result['source']}) {result['text'][:80]}...")
        print()