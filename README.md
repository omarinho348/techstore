# TechStore AI Customer Support Assistant

A tool-calling AI customer support assistant for a fictional electronics
retailer, TechStore. Built with the OpenAI Python SDK (Structured
Outputs / strict function calling), Gradio, python-dotenv, and Resend.

The assistant can check order status, search products, cancel eligible
orders, check refund eligibility, look up support tickets, and escalate
unresolved issues to a human support team via email.

---

## Features

- **Six tools**, each backed by real (in-memory, fake) data:
  - `check_order_status(order_id)`
  - `search_products(keyword)` — case-insensitive, partial, plural-tolerant
  - `cancel_order(order_id)` — enforces cancellation business rules
  - `check_refund_eligibility(order_id)`
  - `ticket_inquiry(ticket_id)`
  - `send_support_email(customer_email, issue)` — last-resort escalation only
- **Structured Outputs** (`strict: true`) on every tool schema, guaranteeing
  well-formed tool call arguments.
- A system prompt that enforces: always use tools for facts, never invent
  data, and only escalate via email when nothing else can resolve the issue.
- A Gradio chat UI (`ChatInterface`) with example prompts.

---

## Project Structure

```
week2-workshop2/
│
├── main.py              # Orchestration: OpenAI client, system prompt,
│                         # tool-calling loop, Gradio app
├── tools.py              # Business logic: the six tool functions
├── schemas.py             # OpenAI tool schemas (Structured Outputs)
├── fake_database.json     # In-memory mock data (orders, products, tickets)
├── .env                   # API keys (NOT committed to version control)
├── .gitignore
├── README.md
└── pyproject.toml
```

---

## Setup

### 1. Clone and create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate      # on Windows: .venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -e .
```

(or manually: `pip install openai gradio python-dotenv resend`)

### 3. Configure environment variables

Edit `.env` and fill in your real keys:

```
OPENAI_API_KEY=your-openai-key-here
RESEND_API_KEY=your-resend-key-here
SUPPORT_TEAM_EMAIL=your-resend-signup-email@example.com
```

- Get an OpenAI key from https://platform.openai.com/api-keys
- Get a Resend key from https://resend.com/api-keys
- `SUPPORT_TEAM_EMAIL` must match the email address you signed up to
  Resend with — the sandbox sender (`onboarding@resend.dev`) can only
  deliver to that address until you verify your own domain.

**Never commit `.env`.** It's already listed in `.gitignore`.

### 4. Confirm your OpenAI model access

Your OpenAI project may not have access to every model. Check
`main.py`'s `OPENAI_MODEL` constant and update it to a model your key
can use if you hit a `403 model_not_found` error.

### 5. Run the app

```bash
python main.py
```

This opens the Gradio chat UI in your browser (typically at
`http://127.0.0.1:7860`).

---

## Business Rules

- **Order cancellation:** only `Processing` orders can be cancelled.
  `Shipped`, `Delivered`, and already-`Cancelled` orders are rejected
  with a clear explanation.
- **Email escalation:** the assistant is instructed (both in its system
  prompt and in the `send_support_email` tool description) to use this
  only as a last resort, after the other five tools have failed to
  resolve the issue.

---

## Sample Data

`fake_database.json` includes:

- **4 orders** (`1001`–`1004`) covering each status: Processing, Shipped,
  Delivered, Cancelled.
- **5 products** across Laptop, Phone, and Accessories categories.
- **2 support tickets** (`T-5001`, `T-5002`).

Feel free to edit this file directly to add more test data — no code
changes required, since `tools.py` loads it dynamically at startup.

---

## Notes

- This version uses an **in-memory fake database** (a JSON file loaded
  once at startup). A real database (PostgreSQL + SQLAlchemy) is planned
  for a later iteration — the tool functions are written so that
  swapping the data layer won't change how the model calls them.
- Order mutations (e.g., a successful cancellation) persist only for the
  lifetime of the running process — restarting the app reloads
  `fake_database.json` fresh from disk.