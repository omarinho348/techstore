"""
test_email.py

Standalone script to verify Resend email sending works BEFORE wiring it
into the AI assistant. Run this directly:

    python test_email.py

Delete this file once you've confirmed emails are sending correctly --
it's a debugging tool, not part of the final application.
"""

from tools import send_support_email

if __name__ == "__main__":
    result = send_support_email(
        customer_email="test.customer@example.com",
        issue="Test escalation -- I was charged twice for the same order.",
    )
    print(result)

    if result["success"]:
        print("\nSuccess! Check your inbox (the address in SUPPORT_TEAM_EMAIL).")
    else:
        print("\nSomething went wrong. Check the error message above, and confirm:")
        print("  1. RESEND_API_KEY is set correctly in .env")
        print("  2. SUPPORT_TEAM_EMAIL matches the address you signed up with on Resend")