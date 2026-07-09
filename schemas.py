"""
schemas.py

This module defines the JSON Schema "shape" of each tool, exactly as the
OpenAI API expects them. These schemas are METADATA -- they describe
what tools exist and what arguments they need, but contain no logic
themselves. The actual implementations live in tools.py.

Every schema uses Structured Outputs (strict=True), which guarantees the
model's tool-call arguments will always match the schema exactly -- no
missing fields, no wrong types, no hallucinated extra fields.
"""

from typing import Any

# =====================================================================
# TOOL SCHEMA: check_order_status
# =====================================================================
CHECK_ORDER_STATUS_SCHEMA: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "check_order_status",
        "description": (
            "Look up an order by its ID and return its current status "
            "(Processing, Shipped, Delivered, or Cancelled), payment "
            "state, and total. Use this whenever a customer asks about "
            "the status of an order they placed."
        ),
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order ID to look up, e.g. '1001'.",
                }
            },
            "required": ["order_id"],
            "additionalProperties": False,
        },
    },
}


# =====================================================================
# TOOL SCHEMA: search_products
# =====================================================================
SEARCH_PRODUCTS_SCHEMA: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "search_products",
        "description": (
            "Search the TechStore product catalog by keyword. Matches "
            "against both product name and category, case-insensitively, "
            "using partial matching. Use this when a customer asks about "
            "product availability, pricing, or wants recommendations."
        ),
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "Search term, e.g. 'laptop', 'iphone', 'accessories'.",
                }
            },
            "required": ["keyword"],
            "additionalProperties": False,
        },
    },
}


# =====================================================================
# TOOL SCHEMA: cancel_order
# =====================================================================
CANCEL_ORDER_SCHEMA: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "cancel_order",
        "description": (
            "Cancel an order by its ID. Only orders with status "
            "'Processing' can be cancelled -- orders that are 'Shipped' "
            "or 'Delivered' cannot be cancelled. Use this only when the "
            "customer explicitly asks to cancel an order."
        ),
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order ID to cancel, e.g. '1001'.",
                }
            },
            "required": ["order_id"],
            "additionalProperties": False,
        },
    },
}


# =====================================================================
# TOOL SCHEMA: check_refund_eligibility
# =====================================================================
CHECK_REFUND_ELIGIBILITY_SCHEMA: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "check_refund_eligibility",
        "description": (
            "Check whether an order is eligible for a refund. Use this "
            "when a customer asks if they can get their money back for "
            "an order."
        ),
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order ID to check, e.g. '1001'.",
                }
            },
            "required": ["order_id"],
            "additionalProperties": False,
        },
    },
}


# =====================================================================
# TOOL SCHEMA: ticket_inquiry
# =====================================================================
TICKET_INQUIRY_SCHEMA: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "ticket_inquiry",
        "description": (
            "Look up an existing support ticket by its ticket ID and "
            "return its subject, status, and creation date. Use this "
            "when a customer asks about the status of a support ticket "
            "they already opened."
        ),
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "ticket_id": {
                    "type": "string",
                    "description": "The support ticket ID, e.g. 'T-5001'.",
                }
            },
            "required": ["ticket_id"],
            "additionalProperties": False,
        },
    },
}


# =====================================================================
# TOOL SCHEMA: send_support_email
# =====================================================================
SEND_SUPPORT_EMAIL_SCHEMA: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "send_support_email",
        "description": (
            "Escalate an unresolved customer issue to the human support "
            "team via email. ONLY call this tool when none of the other "
            "five tools (check_order_status, search_products, "
            "cancel_order, check_refund_eligibility, ticket_inquiry) can "
            "resolve the customer's issue -- for example, a duplicate "
            "charge complaint or a problem requiring human judgment. Do "
            "not use this as a first resort."
        ),
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "customer_email": {
                    "type": "string",
                    "description": "The customer's email address, so support can reply.",
                },
                "issue": {
                    "type": "string",
                    "description": "A clear description of the unresolved issue.",
                },
            },
            "required": ["customer_email", "issue"],
            "additionalProperties": False,
        },
    },
}


# =====================================================================
# ALL SCHEMAS, COLLECTED
# =====================================================================
# main.py imports this single list and passes it directly into the
# `tools` parameter of the chat completions call.
ALL_TOOL_SCHEMAS: list[dict[str, Any]] = [
    CHECK_ORDER_STATUS_SCHEMA,
    SEARCH_PRODUCTS_SCHEMA,
    CANCEL_ORDER_SCHEMA,
    CHECK_REFUND_ELIGIBILITY_SCHEMA,
    TICKET_INQUIRY_SCHEMA,
    SEND_SUPPORT_EMAIL_SCHEMA,
]