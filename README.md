# TechStore AI Customer Support Assistant

A tool-calling AI customer support assistant for a fictional electronics
retailer, TechStore. Built with the OpenAI Python SDK (Structured
Outputs / strict function calling), Gradio, python-dotenv, Resend, and
Chroma (for retrieval-augmented generation).

The assistant can check order status, search products, cancel eligible
orders, check refund eligibility, look up support tickets, escalate
unresolved issues to a human support team via email, and answer
open-ended policy/FAQ questions (return policy, warranty, shipping,
store info) using a small RAG pipeline over a local knowledge base.

---

## Features

- **Seven tools**, six backed by structured (in-memory, fake) data and
  one backed by retrieval over a document knowledge base:
  - `check_order_status(order_id)`
  - `search_products(keyword)` — case-insensitive, partial, plural-tolerant
  - `cancel_order(order_id)` — enforces cancellation business rules
  - `check_refund_eligibility(order_id)`
  - `ticket_inquiry(ticket_id)`
  - `send_support_email(customer_email, issue)` — last-resort escalation only
  - `search_knowledge_base(query)` — RAG over policy/FAQ documents (return
    policy, warranty, shipping, store info, general FAQ)
- **Structured Outputs** (`strict: true`) on every tool schema, guaranteeing
  well-formed tool call arguments.
- A system prompt that enforces: always use tools for facts, never invent
  data, route policy questions to the knowledge base and record lookups to
  the matching backend tool (a single question can trigger both), and only
  escalate via email when nothing else can resolve the issue.
- A **RAG pipeline** (`rag.py`): documents are chunked, embedded with
  OpenAI (`text-embedding-3-small`), stored in a local persistent Chroma
  collection, and retrieved by a calibrated similarity-distance threshold
  — so genuinely irrelevant questions correctly come back empty instead
  of being answered from an unrelated policy chunk.
- A Gradio chat UI (`ChatInterface`) with a dark custom theme, streaming
  "typing" responses, custom avatars, and example prompts.

---

## Project Structure

```
techstore/
│
├── main.py                # Orchestration: OpenAI client, system prompt,
│                           # tool-calling loop, Gradio app + UI styling
├── tools.py                # Business logic: the seven tool functions
├── schemas.py               # OpenAI tool schemas (Structured Outputs)
├── rag.py                   # RAG pipeline: chunking, embeddings, Chroma
│                             # storage, calibrated-threshold retrieval
├── fake_database.json       # In-memory mock data (orders, products, tickets)
├── knowledge_base/           # Plain-text policy/FAQ source documents
│   ├── return_policy.txt
│   ├── warranty.txt
│   ├── shipping_policy.txt
│   ├── store_information.txt
│   └── faq.txt
├── chroma_store/              # Generated: persisted vector store
│                               # (git-ignored, rebuilt from knowledge_base/)
├── assets/                    # Generated chat UI avatar images
│   ├── user_avatar.png
│   └── bot_avatar.png
├── .env                      # API keys (NOT committed to version control)
├── .gitignore
├── README.md
└── pyproject.toml
```

Your knowledge base filenames may differ from the list above if you're
using your own mentor-provided documents — `rag.py` loads whatever
`.txt` files are present in `knowledge_base/`, no hardcoded filenames.

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

(or manually: `pip install openai gradio python-dotenv resend chromadb`)

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

### 5. Build the knowledge base (first run only)

The first time you run the app (or `search_knowledge_base` is called),
`rag.py` embeds every chunk in `knowledge_base/*.txt` via the OpenAI
embeddings API and stores them in a local `chroma_store/` folder. This
costs a small number of embedding API calls, but only happens once —
subsequent runs detect the existing collection and skip re-embedding.

If you edit or add files in `knowledge_base/`, delete `chroma_store/`
first to force a fresh embed; otherwise the app keeps serving the old,
now-stale data.

### 6. Run the app

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
  only as a last resort, after the other six tools have failed to
  resolve the issue.
- **Knowledge base vs. backend routing:** the system prompt tells the
  model to use `search_knowledge_base` for open-ended policy/FAQ
  questions not tied to a specific record, and the matching backend
  tool when a question references a specific order/product/ticket ID.
  A single question can trigger both in the same turn (e.g., "what's
  your return policy, and is order 1003 eligible for a refund?").
- **Relevance threshold:** `search_knowledge_base` only returns chunks
  within a calibrated similarity-distance cutoff (`MAX_RELEVANT_DISTANCE`
  in `rag.py`). Genuinely unrelated questions correctly come back empty
  (`found: false`) rather than being answered from a mismatched chunk.

---

## Sample Data

`fake_database.json` includes:

- **4 orders** (`1001`–`1004`) covering each status: Processing, Shipped,
  Delivered, Cancelled.
- **5 products** across Laptop, Phone, and Accessories categories.
- **2 support tickets** (`T-5001`, `T-5002`).

Feel free to edit this file directly to add more test data — no code
changes required, since `tools.py` loads it dynamically at startup.

`knowledge_base/` contains short plain-text policy/FAQ documents (return
policy, warranty, shipping, store information, and general FAQ). Each
document is chunked on blank lines, so keep related content in
paragraph form for the chunking to stay meaningful — see `rag.py`'s
`chunk_text()`.

---

## Notes

- This version uses an **in-memory fake database** (a JSON file loaded
  once at startup). A real database (PostgreSQL + SQLAlchemy) is planned
  for a later iteration — the tool functions are written so that
  swapping the data layer won't change how the model calls them.
- Order mutations (e.g., a successful cancellation) persist only for the
  lifetime of the running process — restarting the app reloads
  `fake_database.json` fresh from disk.
- The RAG pipeline uses Chroma and the OpenAI embeddings API directly,
  rather than a higher-level library like EmbedChain — for a knowledge
  base this small, direct calls keep the pipeline transparent and easy
  to debug (see `rag.py`) without adding an abstraction layer.