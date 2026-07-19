"""
tools.py

This module contains the business logic for the TechStore AI Customer
Support Assistant. Every function here is a "tool" that the OpenAI model
can call to perform a real action: look up an order, search products,
cancel an order, check refund eligibility, look up a ticket, or escalate
an issue via email.

None of the functions in this file know anything about OpenAI, chat
messages, or tool-calling protocol. They are plain Python functions that
take simple arguments and return dictionaries. This separation means we
can unit test this file in complete isolation from the AI layer.
"""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import resend
from dotenv import load_dotenv

from rag import retrieve_relevant_chunks

# Load environment variables from .env (OPENAI_API_KEY, RESEND_API_KEY, etc.)
load_dotenv()

# =====================================================================
# LOGGING SETUP
# =====================================================================
# We use the `logging` module instead of `print()` so that output can be
# filtered, redirected, or silenced later without touching business logic.
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# =====================================================================
# DATABASE LOADING
# =====================================================================
# Path to the fake database file. Using Path(__file__).parent ensures
# this works no matter what directory the script is *run* from, not just
# where it lives.
DATABASE_PATH = Path(__file__).parent / "fake_database.json"


def load_database() -> dict[str, Any]:
    """
    Load the fake database from fake_database.json into memory.

    This function is intentionally simple: it reads the JSON file once
    and returns its contents as a Python dictionary. In a real production
    system, this function is the ONLY place you'd need to change to swap
    in a real database (e.g., replace the file read with a SQL query) —
    every tool function below would stay exactly the same.

    Returns:
        A dictionary with three keys: "orders", "products", "tickets".

    Raises:
        FileNotFoundError: If fake_database.json does not exist.
        json.JSONDecodeError: If the file exists but contains invalid JSON.
    """
    try:
        with open(DATABASE_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)
        logger.info("Fake database loaded successfully from %s", DATABASE_PATH)
        return data
    except FileNotFoundError:
        logger.error("Database file not found at %s", DATABASE_PATH)
        raise
    except json.JSONDecodeError as error:
        logger.error("Database file contains invalid JSON: %s", error)
        raise


# Load the database once, at import time. Every tool function below reads
# from this in-memory copy instead of re-reading the file on every call.
DATABASE: dict[str, Any] = load_database()


# =====================================================================
# TOOL 1: CHECK ORDER STATUS
# =====================================================================
def check_order_status(order_id: str) -> dict[str, Any]:
    """
    Look up an order and return its status, payment state, and total.

    Args:
        order_id: The order ID to look up (e.g., "1001"). Accepts either
            a string or an int-like value; it will be normalized to str
            since our database keys are strings.

    Returns:
        On success:
            {
                "found": True,
                "order_id": "1001",
                "status": "Processing",
                "payment": "Paid",
                "total": 799
            }
        On failure (order not found):
            {
                "found": False,
                "order_id": "9999",
                "error": "No order found with ID 9999."
            }
    """
    normalized_id = str(order_id)
    order = DATABASE["orders"].get(normalized_id)

    if order is None:
        logger.info("check_order_status: order %s not found", normalized_id)
        return {
            "found": False,
            "order_id": normalized_id,
            "error": f"No order found with ID {normalized_id}.",
        }

    logger.info("check_order_status: order %s found (status=%s)", normalized_id, order["status"])
    return {
        "found": True,
        "order_id": normalized_id,
        "status": order["status"],
        "payment": order["payment"],
        "total": order["total"],
    }


# =====================================================================
# TOOL 2: SEARCH PRODUCTS
# =====================================================================
def _text_matches(keyword: str, field: str) -> bool:
    """
    Check whether a normalized keyword matches a normalized field value,
    tolerating simple singular/plural differences (e.g. "phones" should
    match "Phone").

    This is intentionally lightweight -- just substring matching plus a
    naive trailing-"s" strip -- rather than a full stemming library,
    which would be overkill for this workshop's scope.

    Args:
        keyword: Already-lowercased search keyword.
        field: Already-lowercased product name or category.

    Returns:
        True if the keyword and field are considered a match.
    """
    if keyword in field or field in keyword:
        return True

    keyword_singular = keyword[:-1] if keyword.endswith("s") else keyword
    field_singular = field[:-1] if field.endswith("s") else field
    return keyword_singular in field_singular or field_singular in keyword_singular


def search_products(keyword: str) -> dict[str, Any]:
    """
    Search products by name or category using case-insensitive partial
    matching, tolerant of simple singular/plural differences.

    Args:
        keyword: The search term (e.g., "laptop", "iphone", "phones").
            Matching is case-insensitive and partial -- "lap" will match
            "MacBook Air M3" only if "lap" appears in its name/category,
            but "top" will match "Laptop" as a category. Plural forms
            like "phones" also match singular fields like "Phone".

    Returns:
        {
            "found": True,
            "keyword": "phones",
            "results": [ {...product...}, {...product...} ]
        }
        or, if nothing matches:
        {
            "found": False,
            "keyword": "drone",
            "results": [],
            "error": "No products found matching 'drone'."
        }
    """
    normalized_keyword = keyword.strip().lower()

    matches = [
        product
        for product in DATABASE["products"]
        if _text_matches(normalized_keyword, product["name"].lower())
        or _text_matches(normalized_keyword, product["category"].lower())
    ]

    if not matches:
        logger.info("search_products: no matches for '%s'", keyword)
        return {
            "found": False,
            "keyword": keyword,
            "results": [],
            "error": f"No products found matching '{keyword}'.",
        }

    logger.info("search_products: %d match(es) for '%s'", len(matches), keyword)
    return {
        "found": True,
        "keyword": keyword,
        "results": matches,
    }


# =====================================================================
# TOOL 3: CANCEL ORDER
# =====================================================================
def cancel_order(order_id: str) -> dict[str, Any]:
    """
    Cancel an order, enforcing TechStore's cancellation business rules.

    Business rules (per workshop spec):
        - Orders with status "Processing" CAN be cancelled.
        - Orders with status "Shipped" or "Delivered" CANNOT be cancelled.
        - Orders already "Cancelled" cannot be cancelled again.

    Args:
        order_id: The order ID to cancel.

    Returns:
        {
            "success": True,
            "order_id": "1001",
            "message": "Order 1001 has been cancelled."
        }
        or, on failure:
        {
            "success": False,
            "order_id": "1002",
            "error": "Order 1002 cannot be cancelled because it has already been Shipped."
        }
    """
    normalized_id = str(order_id)
    order = DATABASE["orders"].get(normalized_id)

    if order is None:
        logger.info("cancel_order: order %s not found", normalized_id)
        return {
            "success": False,
            "order_id": normalized_id,
            "error": f"No order found with ID {normalized_id}.",
        }

    current_status = order["status"]

    if current_status in ("Shipped", "Delivered"):
        logger.info("cancel_order: order %s cannot be cancelled (status=%s)", normalized_id, current_status)
        return {
            "success": False,
            "order_id": normalized_id,
            "error": f"Order {normalized_id} cannot be cancelled because it has already been {current_status}.",
        }

    if current_status == "Cancelled":
        logger.info("cancel_order: order %s already cancelled", normalized_id)
        return {
            "success": False,
            "order_id": normalized_id,
            "error": f"Order {normalized_id} has already been cancelled.",
        }

    # Only "Processing" orders reach this point.
    order["status"] = "Cancelled"
    logger.info("cancel_order: order %s successfully cancelled", normalized_id)
    return {
        "success": True,
        "order_id": normalized_id,
        "message": f"Order {normalized_id} has been cancelled.",
    }


# =====================================================================
# TOOL 4: CHECK REFUND ELIGIBILITY
# =====================================================================
def check_refund_eligibility(order_id: str) -> dict[str, Any]:
    """
    Check whether an order is eligible for a refund.

    Args:
        order_id: The order ID to check.

    Returns:
        {
            "found": True,
            "order_id": "1001",
            "eligible_refund": True
        }
        or, if the order doesn't exist:
        {
            "found": False,
            "order_id": "9999",
            "error": "No order found with ID 9999."
        }
    """
    normalized_id = str(order_id)
    order = DATABASE["orders"].get(normalized_id)

    if order is None:
        logger.info("check_refund_eligibility: order %s not found", normalized_id)
        return {
            "found": False,
            "order_id": normalized_id,
            "error": f"No order found with ID {normalized_id}.",
        }

    logger.info(
        "check_refund_eligibility: order %s eligible=%s",
        normalized_id,
        order["eligible_refund"],
    )
    return {
        "found": True,
        "order_id": normalized_id,
        "eligible_refund": order["eligible_refund"],
    }


# =====================================================================
# TOOL 5: TICKET INQUIRY
# =====================================================================
def ticket_inquiry(ticket_id: str) -> dict[str, Any]:
    """
    Look up an existing support ticket by its ID.

    Args:
        ticket_id: The ticket ID to look up (e.g., "T-5001").

    Returns:
        {
            "found": True,
            "ticket_id": "T-5001",
            "subject": "Laptop screen flickering",
            "status": "Open",
            "created_at": "2026-06-28"
        }
        or, if not found:
        {
            "found": False,
            "ticket_id": "T-9999",
            "error": "No ticket found with ID T-9999."
        }
    """
    normalized_id = str(ticket_id).strip().upper()

    ticket = next(
        (t for t in DATABASE["tickets"] if t["ticket_id"].upper() == normalized_id),
        None,
    )

    if ticket is None:
        logger.info("ticket_inquiry: ticket %s not found", normalized_id)
        return {
            "found": False,
            "ticket_id": normalized_id,
            "error": f"No ticket found with ID {normalized_id}.",
        }

    logger.info("ticket_inquiry: ticket %s found (status=%s)", normalized_id, ticket["status"])
    return {
        "found": True,
        "ticket_id": ticket["ticket_id"],
        "subject": ticket["subject"],
        "status": ticket["status"],
        "created_at": ticket["created_at"],
    }


# =====================================================================
# TOOL 6: SEND SUPPORT EMAIL (ESCALATION)
# =====================================================================
# Environment variable names as constants, so a typo only needs fixing
# in one place.
RESEND_API_KEY_ENV = "RESEND_API_KEY"
SUPPORT_TEAM_EMAIL_ENV = "SUPPORT_TEAM_EMAIL"

resend.api_key = os.environ.get(RESEND_API_KEY_ENV)


def send_support_email(customer_email: str, issue: str) -> dict[str, Any]:
    """
    Escalate an unresolved customer issue to the human support team via
    email (using Resend's sandbox sender).

    This tool should ONLY be called by the model when none of the other
    five tools can resolve the customer's issue (e.g., a duplicate charge
    complaint, a complex complaint requiring human judgment).

    Args:
        customer_email: The customer's email address, so support can
            reply directly.
        issue: A description of the issue that could not be resolved
            automatically.

    Returns:
        {
            "success": True,
            "message": "Your issue has been escalated to our support team."
        }
        or, on failure:
        {
            "success": False,
            "error": "<description of what went wrong>"
        }
    """
    support_team_email = os.environ.get(SUPPORT_TEAM_EMAIL_ENV)

    if not resend.api_key or not support_team_email:
        logger.error("send_support_email: missing RESEND_API_KEY or SUPPORT_TEAM_EMAIL in environment")
        return {
            "success": False,
            "error": "Email escalation is not configured. Missing RESEND_API_KEY or SUPPORT_TEAM_EMAIL.",
        }

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    email_params = {
        "from": "TechStore Assistant <onboarding@resend.dev>",
        "to": [support_team_email],
        "subject": f"Escalation: Unresolved issue from {customer_email}",
        "html": (
            f"<p><strong>Customer email:</strong> {customer_email}</p>"
            f"<p><strong>Reported at:</strong> {timestamp}</p>"
            f"<p><strong>Issue:</strong></p>"
            f"<p>{issue}</p>"
        ),
    }

    try:
        response = resend.Emails.send(email_params)
        logger.info("send_support_email: escalation email sent (id=%s)", response.get("id"))
        return {
            "success": True,
            "message": "Your issue has been escalated to our support team.",
        }
    except Exception as error:  # Resend SDK can raise various exception types
        logger.error("send_support_email: failed to send email: %s", error)
        return {
            "success": False,
            "error": f"Failed to send escalation email: {error}",
        }


# =====================================================================
# TOOL 7: SEARCH KNOWLEDGE BASE (RAG)
# =====================================================================
def search_knowledge_base(query: str) -> dict[str, Any]:
    """
    Search TechStore's knowledge base (return policy, warranty, shipping,
    store information, and FAQ documents) for information relevant to a
    customer's question.

    This is a RAG (Retrieval-Augmented Generation) tool: it embeds the
    query and retrieves the most semantically similar chunk(s) from a
    Chroma vector store built from knowledge_base/*.txt. Unlike the
    other tools, it doesn't look up a specific record by ID -- it
    answers open-ended policy/FAQ questions that live in documents, not
    in structured order/product/ticket data.

    Args:
        query: The customer's question, in natural language (e.g.,
            "What's your return policy?", "Is water damage covered
            under warranty?").

    Returns:
        On success (at least one relevant chunk found):
            {
                "found": True,
                "query": "What's your return policy?",
                "results": [
                    {"text": "...", "source": "return_policy.txt"},
                    ...
                ]
            }
        On failure (nothing relevant enough in the knowledge base):
            {
                "found": False,
                "query": "...",
                "results": [],
                "error": "No relevant information found for '...'."
            }
    """
    relevant_chunks = retrieve_relevant_chunks(query)

    if not relevant_chunks:
        logger.info("search_knowledge_base: no relevant chunks for query %r", query)
        return {
            "found": False,
            "query": query,
            "results": [],
            "error": f"No relevant information found for '{query}'.",
        }

    logger.info(
        "search_knowledge_base: %d relevant chunk(s) found for query %r",
        len(relevant_chunks),
        query,
    )
    return {
        "found": True,
        "query": query,
        "results": relevant_chunks,
    }