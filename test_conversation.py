"""
test_conversation.py

Standalone script to verify the full tool-calling loop works end-to-end
with a real OpenAI API call. Run this directly:

    python test_conversation.py

Delete this file once you've confirmed it works -- it's a debugging
tool, not part of the final application.
"""

from main import SYSTEM_PROMPT, get_assistant_response

if __name__ == "__main__":
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    test_questions = [
        "What's the status of order 1001?",
        "Can I cancel order 1002?",
        "Do you have any laptops in stock?",
    ]

    for question in test_questions:
        print(f"\nUser: {question}")
        messages.append({"role": "user", "content": question})
        reply = get_assistant_response(messages)
        print(f"Assistant: {reply}")