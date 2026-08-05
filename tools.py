"""
tools.py

Business logic tools for the TechStore AI Customer Support Assistant.

These tools use the same MongoDB database as the FastAPI backend.
This ensures that chatbot operations and REST API operations always
see the same customers, products, and orders.
"""

import logging
import os
from datetime import datetime, timezone
from typing import Any

import resend
from beanie import PydanticObjectId
from dotenv import load_dotenv

from api.models.customer import Customer
from api.models.order import Order, OrderStatus
from api.models.product import Product
from api.models.ticket import Ticket
from rag import retrieve_relevant_chunks

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# =====================================================================
# HELPER: FIND ORDER
# =====================================================================

async def _find_order(order_id: str) -> Order | None:
    """
    Find an order in MongoDB by its Beanie ObjectId string.
    """

    try:
        object_id = PydanticObjectId(order_id)
    except Exception:
        return None

    return await Order.get(object_id)


# =====================================================================
# TOOL 1: CHECK ORDER STATUS
# =====================================================================

async def check_order_status(order_id: str) -> dict[str, Any]:
    """
    Look up an order in MongoDB and return its status and total.

    Args:
        order_id: MongoDB order ID as a string.

    Returns:
        Dictionary containing order status and total, or a not-found
        response.
    """

    normalized_id = str(order_id).strip()

    order = await _find_order(normalized_id)

    if order is None:
        logger.info(
            "check_order_status: order %s not found",
            normalized_id,
        )

        return {
            "found": False,
            "order_id": normalized_id,
            "error": f"No order found with ID {normalized_id}.",
        }

    logger.info(
        "check_order_status: order %s found (status=%s)",
        normalized_id,
        order.status.value,
    )

    return {
        "found": True,
        "order_id": normalized_id,
        "status": order.status.value,
        "total": order.total,
    }


# =====================================================================
# TOOL 2: SEARCH PRODUCTS
# =====================================================================

async def search_products(keyword: str) -> dict[str, Any]:
    """
    Search MongoDB products by name or category.

    Matching is case-insensitive and uses partial matching.

    Args:
        keyword: Product name or category keyword.

    Returns:
        Matching products and their stock information.
    """

    normalized_keyword = keyword.strip().lower()

    products = await Product.find_all().to_list()

    matches = [
        product
        for product in products
        if (
            normalized_keyword in product.name.lower()
            or normalized_keyword in product.category.lower()
        )
    ]

    if not matches:
        logger.info(
            "search_products: no matches for '%s'",
            keyword,
        )

        return {
            "found": False,
            "keyword": keyword,
            "results": [],
            "error": f"No products found matching '{keyword}'.",
        }

    results = [
        {
            "id": str(product.id),
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "category": product.category,
            "stock": product.stock,
        }
        for product in matches
    ]

    logger.info(
        "search_products: %d match(es) for '%s'",
        len(results),
        keyword,
    )

    return {
        "found": True,
        "keyword": keyword,
        "results": results,
    }


# =====================================================================
# TOOL 3: CANCEL ORDER
# =====================================================================

async def cancel_order(order_id: str) -> dict[str, Any]:
    """
    Cancel an order in MongoDB.

    Only orders with status "processing" can be cancelled.

    Args:
        order_id: MongoDB order ID as a string.

    Returns:
        Success or failure result.
    """

    normalized_id = str(order_id).strip()

    order = await _find_order(normalized_id)

    if order is None:
        logger.info(
            "cancel_order: order %s not found",
            normalized_id,
        )

        return {
            "success": False,
            "order_id": normalized_id,
            "error": f"No order found with ID {normalized_id}.",
        }

    current_status = order.status

    if current_status == OrderStatus.SHIPPED:
        return {
            "success": False,
            "order_id": normalized_id,
            "error": (
                f"Order {normalized_id} cannot be cancelled "
                "because it has already been shipped."
            ),
        }

    if current_status == OrderStatus.DELIVERED:
        return {
            "success": False,
            "order_id": normalized_id,
            "error": (
                f"Order {normalized_id} cannot be cancelled "
                "because it has already been delivered."
            ),
        }

    if current_status == OrderStatus.CANCELLED:
        return {
            "success": False,
            "order_id": normalized_id,
            "error": (
                f"Order {normalized_id} has already been cancelled."
            ),
        }

    if current_status != OrderStatus.PROCESSING:
        return {
            "success": False,
            "order_id": normalized_id,
            "error": (
                f"Order {normalized_id} cannot be cancelled "
                f"because its current status is "
                f"{current_status.value}."
            ),
        }

    order.status = OrderStatus.CANCELLED
    order.updated_at = datetime.now(timezone.utc)

    await order.save()

    logger.info(
        "cancel_order: order %s successfully cancelled",
        normalized_id,
    )

    return {
        "success": True,
        "order_id": normalized_id,
        "message": (
            f"Order {normalized_id} has been cancelled."
        ),
    }


# =====================================================================
# TOOL 4: CHECK REFUND ELIGIBILITY
# =====================================================================

async def check_refund_eligibility(
    order_id: str,
) -> dict[str, Any]:
    """
    Check whether an order is eligible for a refund.

    The current Order model does not contain an explicit
    eligible_refund field, so eligibility is determined from the
    order status.

    Args:
        order_id: MongoDB order ID as a string.

    Returns:
        Refund eligibility result.
    """

    normalized_id = str(order_id).strip()

    order = await _find_order(normalized_id)

    if order is None:
        logger.info(
            "check_refund_eligibility: order %s not found",
            normalized_id,
        )

        return {
            "found": False,
            "order_id": normalized_id,
            "error": f"No order found with ID {normalized_id}.",
        }

    eligible_refund = order.status in {
        OrderStatus.DELIVERED,
        OrderStatus.CANCELLED,
    }

    logger.info(
        "check_refund_eligibility: order %s eligible=%s",
        normalized_id,
        eligible_refund,
    )

    return {
        "found": True,
        "order_id": normalized_id,
        "status": order.status.value,
        "eligible_refund": eligible_refund,
    }


# =====================================================================
# TOOL 5: TICKET INQUIRY
# =====================================================================

async def ticket_inquiry(ticket_id: str) -> dict[str, Any]:
    """
    Look up a support ticket by its ticket ID.

    Args:
        ticket_id: Support ticket ID, for example "T-5002".

    Returns:
        Ticket information if found, otherwise a not-found response.
    """

    normalized_id = str(ticket_id).strip().upper()

    logger.info(
        "ticket_inquiry: looking up ticket %s",
        normalized_id,
    )

    ticket = await Ticket.find_one(
        Ticket.ticket_id == normalized_id
    )

    if not ticket:
        logger.info(
            "ticket_inquiry: ticket %s not found",
            normalized_id,
        )

        return {
            "found": False,
            "ticket_id": normalized_id,
            "error": (
                f"No ticket found with ID {normalized_id}."
            ),
        }

    logger.info(
        "ticket_inquiry: ticket %s found with status %s",
        normalized_id,
        ticket.status.value,
    )

    return {
        "found": True,
        "ticket_id": ticket.ticket_id,
        "customer_id": ticket.customer_id,
        "subject": ticket.subject,
        "description": ticket.description,
        "status": ticket.status.value,
        "created_at": ticket.created_at.isoformat(),
        "updated_at": ticket.updated_at.isoformat(),
    }


# =====================================================================
# TOOL 6: SEND SUPPORT EMAIL
# =====================================================================

RESEND_API_KEY_ENV = "RESEND_API_KEY"
SUPPORT_TEAM_EMAIL_ENV = "SUPPORT_TEAM_EMAIL"

resend.api_key = os.environ.get(RESEND_API_KEY_ENV)


async def send_support_email(
    customer_email: str,
    issue: str,
) -> dict[str, Any]:
    """
    Escalate an unresolved customer issue to human support via email.

    Args:
        customer_email: Customer's email address.
        issue: Description of the unresolved issue.

    Returns:
        Success or failure result.
    """

    support_team_email = os.environ.get(
        SUPPORT_TEAM_EMAIL_ENV
    )

    if not resend.api_key or not support_team_email:
        logger.error(
            "send_support_email: missing RESEND_API_KEY "
            "or SUPPORT_TEAM_EMAIL"
        )

        return {
            "success": False,
            "error": (
                "Email escalation is not configured. "
                "Missing RESEND_API_KEY or SUPPORT_TEAM_EMAIL."
            ),
        }

    timestamp = datetime.now(
        timezone.utc
    ).strftime("%Y-%m-%d %H:%M:%S UTC")

    email_params = {
        "from": "TechStore Assistant <onboarding@resend.dev>",
        "to": [support_team_email],
        "subject": (
            f"Escalation: Unresolved issue from "
            f"{customer_email}"
        ),
        "html": (
            f"<p><strong>Customer email:</strong> "
            f"{customer_email}</p>"
            f"<p><strong>Reported at:</strong> "
            f"{timestamp}</p>"
            f"<p><strong>Issue:</strong></p>"
            f"<p>{issue}</p>"
        ),
    }

    try:
        response = resend.Emails.send(email_params)

        logger.info(
            "send_support_email: escalation email sent "
            "(id=%s)",
            response.get("id"),
        )

        return {
            "success": True,
            "message": (
                "Your issue has been escalated "
                "to our support team."
            ),
        }

    except Exception as error:
        logger.error(
            "send_support_email: failed to send email: %s",
            error,
        )

        return {
            "success": False,
            "error": (
                f"Failed to send escalation email: {error}"
            ),
        }


# =====================================================================
# TOOL 7: SEARCH KNOWLEDGE BASE
# =====================================================================

async def search_knowledge_base(
    query: str,
) -> dict[str, Any]:
    """
    Search TechStore's knowledge base for policy and FAQ information.

    Args:
        query: Customer's natural-language question.

    Returns:
        Relevant knowledge-base results.
    """

    relevant_chunks = retrieve_relevant_chunks(query)

    if not relevant_chunks:
        logger.info(
            "search_knowledge_base: no relevant chunks "
            "for query %r",
            query,
        )

        return {
            "found": False,
            "query": query,
            "results": [],
            "error": (
                f"No relevant information found "
                f"for '{query}'."
            ),
        }

    logger.info(
        "search_knowledge_base: %d relevant chunk(s) "
        "found for query %r",
        len(relevant_chunks),
        query,
    )

    return {
        "found": True,
        "query": query,
        "results": relevant_chunks,
    }

# =====================================================================
# TOOL 8: GET MY ORDERS
# =====================================================================

async def get_my_orders(customer_email: str):
    """
    Return every order belonging to the authenticated customer.
    """

    customer = await Customer.find_one(
        Customer.email == customer_email
    )

    if customer is None:
        return {
            "found": False,
            "orders": [],
        }

    orders = await Order.find(
        Order.customer_id == str(customer.id)
    ).sort(
        -Order.created_at
    ).to_list()

    order_list = []

    for order in orders:

        items = []

        for item in order.items:

            product = await Product.get(item.product_id)

            items.append(
                {
                    "title": item.product_name,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "subtotal": item.subtotal,
                    "stock": product.stock if product else "Unknown",
                }
            )

        order_list.append(
            {
                "order_id": str(order.id),
                "status": order.status.value,
                "total": order.total,
                "created_at": order.created_at.isoformat(),
                "items": items,
            }
        )

    return {
        "found": True,
        "count": len(order_list),
        "orders": order_list,
    }