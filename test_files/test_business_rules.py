"""
test_business_rules.py

Exercises the full assistant (via chat_function) against every business
rule from the workshop spec. Each test uses a FRESH conversation, so
results don't get influenced by prior turns.

Run this directly:

    python test_business_rules.py

Delete this file once you've confirmed everything passes -- it's a
debugging/verification tool, not part of the final application.
"""

from main import chat_function


def run_test(label: str, message: str) -> None:
    """Run a single test case with a fresh, empty conversation history."""
    print(f"\n{'=' * 70}")
    print(f"TEST: {label}")
    print(f"{'=' * 70}")
    print(f"User: {message}")
    reply = chat_function(message, [])
    print(f"Assistant: {reply}")


if __name__ == "__main__":
    # Order 1001 = Processing -> should succeed
    run_test("Cancel a Processing order (should SUCCEED)", "Please cancel order 1001.")

    # Order 1002 = Shipped -> should fail
    run_test("Cancel a Shipped order (should FAIL)", "Please cancel order 1002.")

    # Order 1003 = Delivered -> should fail
    run_test("Cancel a Delivered order (should FAIL)", "Please cancel order 1003.")

    # Product search
    run_test("Product search", "Do you have any phones available?")

    # Refund eligibility
    run_test("Refund eligibility", "Is order 1003 eligible for a refund?")

    # Ticket lookup
    run_test("Ticket lookup", "What's the status of ticket T-5002?")

    # Email escalation -- an issue no other tool can resolve
    run_test(
        "Email escalation (should call send_support_email)",
        "I was charged twice for the same order and none of my orders show "
        "a duplicate charge -- my email is jane.doe@example.com. Can someone "
        "look into this?",
    )