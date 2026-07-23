"""
agent_team.py

Week 4: Agentic AI. Defines the multi-agent team for the TechStore
assistant using the OpenAI Agents SDK -- three specialist agents, each
scoped to a small subset of the existing tools.py functions, plus a
triage agent that routes customer requests to the right specialist via
handoffs.

Named agent_team.py (not agents.py) to avoid shadowing the installed
`agents` package.

IMPORTANT: this file does not redefine any business logic. Every tool
here is the existing, unmodified function from tools.py, wrapped with
agents.function_tool(), which auto-generates each tool's schema from
that function's existing docstring and type hints. tools.py and rag.py
are untouched.
"""

import os

from agents import Agent, OpenAIChatCompletionsModel, function_tool
from dotenv import load_dotenv
from openai import AsyncOpenAI

from tools import (
    cancel_order,
    check_order_status,
    check_refund_eligibility,
    search_knowledge_base,
    search_products,
    send_support_email,
    ticket_inquiry,
)

load_dotenv()

# =====================================================================
# MODEL CONFIGURATION
# =====================================================================
# The Agents SDK defaults to OpenAI's Responses API (/v1/responses).
# Some API keys (e.g. project-restricted keys) have full access to the
# Chat Completions API -- which this project has used successfully
# since Week 2 -- but lack the newer api.responses.write scope, causing
# a 401 error under the SDK's default configuration.
#
# To avoid depending on a dashboard/key-permission change, we instead
# point every agent at OpenAIChatCompletionsModel, which routes through
# the same /v1/chat/completions endpoint already proven to work.
#
# This model name is duplicated from main.py's OPENAI_MODEL constant
# (rather than imported) to avoid a circular import, since main.py
# imports the triage agent from this file. Keep them in sync.
AGENTS_MODEL_NAME = "gpt-5.4-mini"

_async_openai_client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

_chat_completions_model = OpenAIChatCompletionsModel(
    model=AGENTS_MODEL_NAME,
    openai_client=_async_openai_client,
)

# =====================================================================
# WRAP EXISTING TOOLS (no redefinition -- just schema generation)
# =====================================================================
check_order_status_tool = function_tool(check_order_status)
search_products_tool = function_tool(search_products)
cancel_order_tool = function_tool(cancel_order)
check_refund_eligibility_tool = function_tool(check_refund_eligibility)
ticket_inquiry_tool = function_tool(ticket_inquiry)
send_support_email_tool = function_tool(send_support_email)
search_knowledge_base_tool = function_tool(search_knowledge_base)


# =====================================================================
# KNOWLEDGE AGENT
# =====================================================================
# Tool ONLY: search_knowledge_base. Short, focused instructions -- just
# the rules relevant to RAG-backed policy/FAQ answers, not the full
# Week 2/3 system prompt.
knowledge_agent = Agent(
    name="Knowledge Agent",
    model=_chat_completions_model,
    handoff_description=(
        "Answers open-ended TechStore policy and FAQ questions -- return "
        "policy, warranty, shipping, store hours/locations, general FAQs."
    ),
    instructions=(
        "You are TechStore's Knowledge Agent. You answer questions about "
        "company policy and FAQs (return policy, warranty, shipping, "
        "store hours/locations, general FAQs) using the "
        "search_knowledge_base tool.\n\n"
        "Rules:\n"
        "1. ALWAYS call search_knowledge_base for policy/FAQ questions -- "
        "never guess or invent policy details.\n"
        "2. If the tool returns found: false, tell the customer honestly "
        "that you don't have that information -- do not make something "
        "up.\n"
        "3. Be concise and professional. Summarize the retrieved text in "
        "natural language; don't dump raw tool output.\n"
        "4. If the customer's question also needs order, product, "
        "ticket, or escalation help (something outside policy/FAQ "
        "content), answer the policy part first if you have it, then "
        "hand off to the right specialist for the rest of the question -- "
        "do not just answer half the question and stop."
    ),
    tools=[search_knowledge_base_tool],
)


# =====================================================================
# ORDER & PRODUCT AGENT
# =====================================================================
# Tools ONLY: check_order_status, search_products, cancel_order,
# check_refund_eligibility.
order_product_agent = Agent(
    name="Order  Product Agent",
    model=_chat_completions_model,
    handoff_description=(
        "Handles order status, product search, order cancellation, and "
        "refund eligibility for a specific order."
    ),
    instructions=(
        "You are TechStore's Order & Product Agent. You handle "
        "questions about specific orders and product availability using "
        "your four tools: check_order_status, search_products, "
        "cancel_order, and check_refund_eligibility.\n\n"
        "Rules:\n"
        "1. ALWAYS use a tool for factual lookups -- never guess or "
        "invent an order status, product price, stock level, or refund "
        "eligibility.\n"
        "2. cancel_order enforces business rules server-side (only "
        "Processing orders can be cancelled). If it returns "
        "success: false, relay the reason honestly -- do not retry with "
        "a different value.\n"
        "3. CRITICAL: never tell the customer an order has been "
        "cancelled unless you have just called cancel_order in this "
        "same turn and its result was success: true. Do not describe an "
        "action as completed without actually having called the tool "
        "for it.\n"
        "4. If a tool returns found: false, tell the customer honestly "
        "rather than guessing.\n"
        "5. Be concise and professional. Summarize tool results in "
        "natural language; don't dump raw JSON.\n"
        "6. If the customer's question also needs policy/FAQ "
        "information, a support ticket lookup, or an email escalation "
        "(something outside order/product data), answer the "
        "order/product part first if you have it, then hand off to the "
        "right specialist for the rest -- do not just answer half the "
        "question and stop."
    ),
    tools=[
        check_order_status_tool,
        search_products_tool,
        cancel_order_tool,
        check_refund_eligibility_tool,
    ],
)


# =====================================================================
# SUPPORT AGENT
# =====================================================================
# Tools ONLY: ticket_inquiry, send_support_email.
support_agent = Agent(
    name="Support Agent",
    model=_chat_completions_model,
    handoff_description=(
        "Handles support ticket lookups and escalates unresolved issues "
        "to the human support team via email."
    ),
    instructions="""
You are TechStore's Support Agent.

Your responsibilities include:

- Handling customer support requests.
- Checking support ticket status.
- Escalating customer issues to human support.
- Sending support emails when the customer explicitly requests
  an escalation.

IMPORTANT TOOL RULES:

1. If the customer asks to escalate an issue, you MUST use the
   send_support_email tool.

2. You must not simply tell the customer that the issue was escalated.
   You must actually call send_support_email first.

3. If the customer provides an email address, use that email address
   when calling send_support_email.

4. If the customer provides an email address in the current message,
   do not ignore it.

5. Do not claim that an email was sent unless the send_support_email
   tool actually returned a successful result.

6. If send_support_email fails, clearly tell the customer that the
   escalation could not be completed.

7. If the user asks for an escalation and provides an email address,
   treat that as an explicit request to send the escalation email.

Examples:

User:
"I want to escalate this issue. My email is jane.doe@gmail.com."

Action:
Call send_support_email.

User:
"Please escalate this to support and contact me at jane.doe@gmail.com."

Action:
Call send_support_email.

User:
"I need a human to look into this."

Action:
If an email address is already available in the conversation,
call send_support_email.

If no email address is available, ask the user for their email
address before attempting the escalation.

Never claim that an escalation was completed without actually
calling the send_support_email tool.
""",
    tools=[ticket_inquiry_tool, send_support_email_tool],
)


# =====================================================================
# TRIAGE AGENT
# =====================================================================
# No business tools of its own -- its only job is reading the request
# and routing to the right specialist via a handoff.
triage_agent = Agent(
    name="Triage Agent",
    model=_chat_completions_model,
    instructions="""
You are the central coordinator for TechStore customer support.

Your job is to ensure that EVERY distinct request in the customer's
latest message is fully completed.

IMPORTANT:

A handoff is an internal workflow action.
Never consider a handoff announcement from a specialist to be a
completed task.

For every new user message:

1. Identify every distinct customer intent.
2. Route each intent to the appropriate specialist.
3. Ensure that every identified intent is actually completed.
4. Do not produce a final response until all requested tasks are complete.

Example:

User:
"What is your store phone number and is order 1001 eligible for a refund?"

This contains TWO tasks:

Task 1:
Store phone number
→ Knowledge Agent

Task 2:
Refund eligibility for order 1001
→ Order & Product Agent

The final answer must contain the result of BOTH tasks.

The following is NOT an acceptable final answer:

"TechStore's phone number is ...
For the refund question, I'm handing this off to the Order/Product
specialist."

That response is incomplete.

Instead, the workflow must continue until the Order & Product Agent
has actually processed the refund question.

Only after ALL tasks are completed should a final customer-facing
answer be generated.
""",
    handoffs=[order_product_agent, support_agent, knowledge_agent],
)


# =====================================================================
# SPECIALIST-TO-SPECIALIST HANDOFFS (mesh)
# =====================================================================
# Each specialist can hand off directly to either of the other two,
# without looping back through triage -- this is what lets a single
# conversation move from a policy question (Knowledge Agent) straight
# into an order-specific follow-up (Order & Product Agent) in one turn.
#
# Agent.handoffs is a plain mutable list, so we wire these up after all
# three specialists already exist, avoiding a circular-definition
# problem (each agent would otherwise need to reference the others
# before they're fully constructed).
order_product_agent.handoffs = [support_agent, knowledge_agent]
support_agent.handoffs = [order_product_agent, knowledge_agent]
knowledge_agent.handoffs = [order_product_agent, support_agent]