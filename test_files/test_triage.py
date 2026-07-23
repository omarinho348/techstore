"""
test_files/test_triage.py

Tests the Triage Agent's routing, per the PDF's suggested approach:
1. Each specialist gets picked correctly on its own.
2. A sequential conversation needing two specialists hands off directly
   between them (Knowledge Agent -> Order & Product Agent) in the SAME
   conversation, without restarting.

Run this directly:

    uv run python test_files/test_triage.py

Delete this file (or the whole test_files/ folder) once confirmed --
it's a debugging tool, not part of the final application.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import Runner

from agent_team import triage_agent


def run_single_turn_test(label: str, message: str) -> None:
    """Test that a single, fresh question routes to the right specialist."""
    print(f"\n{'=' * 70}")
    print(f"TEST: {label}")
    print(f"{'=' * 70}")
    print(f"User: {message}")
    result = Runner.run_sync(triage_agent, message)
    print(f"Handled by: {result.last_agent.name}")
    print(f"Assistant: {result.final_output}")


if __name__ == "__main__":
    # --- Single-turn routing tests ---
    run_single_turn_test(
        "Order question -> should route to Order & Product Agent",
        "Where is order 1002?",
    )
    run_single_turn_test(
        "Policy question -> should route to Knowledge Agent",
        "What's your return policy?",
    )
    run_single_turn_test(
        "Ticket question -> should route to Support Agent",
        "What's the status of ticket T-5002?",
    )
    run_single_turn_test(
        "Product search -> should route to Order & Product Agent",
        "Do you have any laptops in stock?",
    )
    run_single_turn_test(
        "Support email issue -> should route to Support Agent",
        "I was charged twice for the same order and none of my orders "
        "show a duplicate charge -- my email is jane.doe@example.com.",
    )

    # --- Multi-specialist sequential conversation (the PDF's exact example) ---
    print(f"\n{'=' * 70}")
    print("TEST: Multi-specialist conversation (same conversation, no restart)")
    print(f"{'=' * 70}")

    print("User: What's your return policy?")
    first_result = Runner.run_sync(triage_agent, "What's your return policy?")
    print(f"Handled by: {first_result.last_agent.name}")
    print(f"Assistant: {first_result.final_output}")

    # Continue the SAME conversation: to_input_list() carries forward the
    # full history (including which agent ended up handling it), so the
    # next turn starts from wherever the conversation left off -- not
    # from triage again.
    follow_up_input = first_result.to_input_list() + [
        {"role": "user", "content": "Given that, is my order 1003 eligible for a refund?"}
    ]

    print("\nUser: Given that, is my order 1003 eligible for a refund?")
    second_result = Runner.run_sync(first_result.last_agent, follow_up_input)
    print(f"Handled by: {second_result.last_agent.name}")
    print(f"Assistant: {second_result.final_output}")

    print("\n--- Verification ---")
    print(f"First turn handled by:  {first_result.last_agent.name} (expected: Knowledge Agent)")
    print(f"Second turn handled by: {second_result.last_agent.name} (expected: Order & Product Agent)")
    print(f"Handoff occurred without restarting: {first_result.last_agent.name != second_result.last_agent.name}")