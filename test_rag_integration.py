"""
test_rag_integration.py

Exercises the full assistant (via chat_function) against the three
required RAG integration cases from the Week 3 workshop, plus one edge
case. Each test uses a FRESH conversation, so results aren't influenced
by prior turns.

Run this directly:

    python test_rag_integration.py

Delete this file once you've confirmed everything passes -- it's a
debugging/verification tool, not part of the final application.
"""

from main import chat_function


def run_test(label: str, message: str) -> None:
    """Run a single test case with a fresh, empty conversation history.

    chat_function is a generator (it streams the reply character-by-
    character for the UI's typing effect), so we must iterate it to
    actually run the underlying logic -- the final yielded value is
    the complete reply.
    """
    print(f"\n{'=' * 70}")
    print(f"TEST: {label}")
    print(f"{'=' * 70}")
    print(f"User: {message}")

    final_reply = ""
    for partial_reply in chat_function(message, []):
        final_reply = partial_reply

    print(f"Assistant: {final_reply}")


if __name__ == "__main__":
    # Case 1: knowledge-base only -- should call search_knowledge_base
    run_test(
        "Knowledge-base only (should call search_knowledge_base)",
        "What's your return policy?",
    )

    # Case 2: backend-only -- should call check_order_status, NOT the KB
    run_test(
        "Backend-only (should call check_order_status)",
        "Where is order 1002?",
    )

    # Case 3: both, in one turn -- the PDF's own example
    run_test(
        "Both KB and backend in one turn (should call both tools)",
        "What's your return policy, and is order 1003 eligible for a refund?",
    )

    # Edge case: genuinely irrelevant question -- should get an honest
    # "I don't know" rather than a misapplied policy chunk
    run_test(
        "Irrelevant question (should NOT confidently answer)",
        "Do you sell scuba diving gear?",
    )