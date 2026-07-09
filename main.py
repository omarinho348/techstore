"""
main.py

This is the orchestration layer of the TechStore AI Customer Support
Assistant. It is the ONLY file that talks to the OpenAI API directly.

Responsibilities of this file:
    - Load environment variables and create the OpenAI client.
    - Hold the system prompt that governs the assistant's behavior.
    - Run the tool-calling loop: send messages to the model, detect tool
      calls, dispatch them to the real functions in tools.py, and send
      results back.
    - Launch the Gradio chat interface.

This file intentionally contains NO business logic (that lives in
tools.py) and NO tool schema definitions (those live in schemas.py).
"""

import json
import logging
import os
import time

import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI

from schemas import ALL_TOOL_SCHEMAS
from tools import (
    cancel_order,
    check_order_status,
    check_refund_eligibility,
    search_products,
    send_support_email,
    ticket_inquiry,
)

# =====================================================================
# ENVIRONMENT SETUP
# =====================================================================
# Load variables from .env into the process environment. This must run
# before we try to read OPENAI_API_KEY below.
load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Constant for the environment variable name, so a typo only needs
# fixing in one place.
OPENAI_API_KEY_ENV = "OPENAI_API_KEY"

# Model used for chat completions. Defined as a constant so it's easy
# to swap later without hunting through the file.
OPENAI_MODEL = "gpt-5.4-mini"


# =====================================================================
# OPENAI CLIENT
# =====================================================================
def create_openai_client() -> OpenAI:
    """
    Create and return an OpenAI client, using the API key from the
    environment.

    Raises:
        ValueError: If OPENAI_API_KEY is not set, so the app fails fast
            with a clear message instead of failing later with a
            confusing authentication error deep inside an API call.
    """
    api_key = os.environ.get(OPENAI_API_KEY_ENV)

    if not api_key:
        raise ValueError(
            f"{OPENAI_API_KEY_ENV} is not set. "
            "Add it to your .env file before running this application."
        )

    logger.info("OpenAI client created successfully.")
    return OpenAI(api_key=api_key)


client = create_openai_client()


# =====================================================================
# SYSTEM PROMPT
# =====================================================================
# This is the behavioral contract for the assistant. It is sent as the
# first message in every conversation and governs how the model uses
# the six tools defined in schemas.py / tools.py.
SYSTEM_PROMPT = """You are the TechStore AI Customer Support Assistant, \
a helpful and professional support agent for TechStore, an online \
electronics retailer.

You have access to six tools that connect to TechStore's real order, \
product, and ticket data. Follow these rules strictly:

1. ALWAYS use a tool for factual lookups. Never guess or make up an \
order status, product price, stock level, refund eligibility, or \
ticket status. If a tool exists that can answer the question, call it.

2. NEVER invent information that was not returned by a tool. If a tool \
result does not include a piece of information (e.g., no tracking \
number), do not fabricate one -- simply state that it is not available.

3. Every tool returns a "found" or "success" field. If it is false, \
tell the customer honestly what went wrong (e.g., "I couldn't find an \
order with that ID") using the tool's error message. Do not retry the \
same tool with a guessed or modified value.

4. Only call send_support_email when NONE of the other five tools \
(check_order_status, search_products, cancel_order, \
check_refund_eligibility, ticket_inquiry) can resolve the customer's \
issue. This is a last resort for problems like duplicate charges, \
complaints, or situations requiring human judgment -- not a first \
response. Before escalating, make sure you've already attempted an \
appropriate tool lookup if one applies to the situation.

5. If the customer's request is missing information a tool requires \
(such as an order ID or ticket ID), ask them for it directly instead \
of guessing or calling the tool with an empty value.

6. Be concise, polite, and professional -- like a real TechStore \
support agent. Summarize tool results in natural language; do not \
dump raw JSON or field names at the customer.
"""


# =====================================================================
# TOOL DISPATCH TABLE
# =====================================================================
# Maps a tool's name (as the model will refer to it) to the actual
# Python function that implements it. This is what lets us go from
# "the model wants to call 'cancel_order'" to actually running
# cancel_order() in tools.py, without a long if/elif chain.
TOOL_DISPATCH: dict[str, callable] = {
    "check_order_status": check_order_status,
    "search_products": search_products,
    "cancel_order": cancel_order,
    "check_refund_eligibility": check_refund_eligibility,
    "ticket_inquiry": ticket_inquiry,
    "send_support_email": send_support_email,
}


# =====================================================================
# TOOL CALL EXECUTION
# =====================================================================
def execute_tool_call(tool_call) -> str:
    """
    Execute a single tool call requested by the model and return its
    result as a JSON string (the format required for tool result
    messages sent back to the API).

    Args:
        tool_call: A tool call object from the model's response,
            containing the function name and its (JSON-string) arguments.

    Returns:
        A JSON-encoded string representing the tool's return value, or
        a JSON-encoded error dict if the tool name is unknown or the
        arguments fail to parse.
    """
    tool_name = tool_call.function.name
    raw_arguments = tool_call.function.arguments

    function_to_call = TOOL_DISPATCH.get(tool_name)
    if function_to_call is None:
        logger.error("execute_tool_call: unknown tool '%s'", tool_name)
        return json.dumps({"error": f"Unknown tool '{tool_name}'."})

    try:
        arguments = json.loads(raw_arguments)
    except json.JSONDecodeError as error:
        logger.error("execute_tool_call: failed to parse arguments for '%s': %s", tool_name, error)
        return json.dumps({"error": f"Invalid arguments for tool '{tool_name}'."})

    logger.info("execute_tool_call: calling %s with %s", tool_name, arguments)
    result = function_to_call(**arguments)
    return json.dumps(result)


# =====================================================================
# MAIN CONVERSATION LOOP
# =====================================================================
def get_assistant_response(conversation_messages: list[dict]) -> str:
    """
    Run one full turn of the tool-calling flow: send the conversation to
    OpenAI, execute any requested tool calls, send results back, and
    return the model's final natural-language reply.

    Args:
        conversation_messages: The full message list so far, starting
            with the system prompt, followed by alternating user/
            assistant messages. This list is mutated in place with any
            tool-call and tool-result messages generated during this turn.

    Returns:
        The assistant's final text reply for this turn.
    """
    # ---- First API call: let the model decide whether to use tools ----
    first_response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=conversation_messages,
        tools=ALL_TOOL_SCHEMAS,
    )
    response_message = first_response.choices[0].message

    # No tool calls -- the model answered directly, we're done.
    if not response_message.tool_calls:
        conversation_messages.append({"role": "assistant", "content": response_message.content})
        return response_message.content

    # ---- The model wants to call one or more tools ----
    # We must append the assistant's tool-call request message itself
    # before appending the tool results, or the API will reject the
    # conversation as malformed.
    conversation_messages.append(response_message)

    for tool_call in response_message.tool_calls:
        tool_result_json = execute_tool_call(tool_call)
        conversation_messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result_json,
            }
        )

    # ---- Second API call: let the model turn tool results into a reply ----
    second_response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=conversation_messages,
    )
    final_message = second_response.choices[0].message
    conversation_messages.append({"role": "assistant", "content": final_message.content})
    return final_message.content


# =====================================================================
# UI ASSETS AND STYLING
# =====================================================================
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
USER_AVATAR_PATH = os.path.join(ASSETS_DIR, "user_avatar.png")
BOT_AVATAR_PATH = os.path.join(ASSETS_DIR, "bot_avatar.png")

# A dark, purple/cyan-accented theme, built on Gradio's base theme so we
# inherit sensible component behavior and only override the palette,
# spacing, and typography we care about.
CUSTOM_THEME = gr.themes.Base(
    primary_hue=gr.themes.colors.purple,
    secondary_hue=gr.themes.colors.cyan,
    neutral_hue=gr.themes.colors.slate,
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
).set(
    body_background_fill="#0f172a",
    body_background_fill_dark="#0f172a",
    background_fill_primary="#111827",
    background_fill_primary_dark="#111827",
    background_fill_secondary="#1e293b",
    background_fill_secondary_dark="#1e293b",
    border_color_primary="#334155",
    border_color_primary_dark="#334155",
    block_background_fill="#111827",
    block_background_fill_dark="#111827",
    block_border_width="1px",
    block_radius="16px",
    button_primary_background_fill="linear-gradient(135deg, #a855f7, #22d3ee)",
    button_primary_background_fill_hover="linear-gradient(135deg, #9333ea, #06b6d4)",
    button_primary_text_color="#0f172a",
    body_text_color="#e2e8f0",
    body_text_color_dark="#e2e8f0",
    body_text_color_subdued="#94a3b8",
)

# Custom CSS for details the theme system doesn't reach: chat bubble
# styling, header glow, scrollbar, and a subtle entrance animation.
CUSTOM_CSS = """
/* Lock the page to the viewport -- no page-level scrollbar. Only the
   chat panel itself (below) is allowed to scroll internally. */
html, body {
    height: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
}

.gradio-container {
    height: 100vh !important;
    max-height: 100vh !important;
    overflow: hidden !important;
    display: flex !important;
    flex-direction: column !important;
    background: radial-gradient(circle at top left, #1e1b4b 0%, #0f172a 45%) !important;
}

/* The main app column should fill available height and lay out its
   children (title, description, chat panel, textbox) vertically,
   letting the chat panel be the flexible element that grows/shrinks. */
.gradio-container > .main,
.gradio-container > div:first-child {
    height: 100% !important;
    min-height: 0 !important;
    display: flex !important;
    flex-direction: column !important;
}

/* Title and description stay fixed-size at the top, never shrinking. */
h1, .prose {
    flex-shrink: 0 !important;
}

/* The chatbot panel grows to fill remaining space and scrolls
   internally once its content exceeds that space. */
.techstore-chatbot {
    flex: 1 1 auto !important;
    min-height: 0 !important;
    overflow-y: auto !important;
}

/* The textbox / submit row stays fixed-size at the bottom. */
form {
    flex-shrink: 0 !important;
}

/* Title styling: gradient text, centered, with a soft glow */
h1 {
    background: linear-gradient(90deg, #c084fc, #67e8f9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
    font-weight: 800 !important;
    letter-spacing: -0.02em;
    filter: drop-shadow(0 0 18px rgba(168, 85, 247, 0.35));
}

/* Description subtitle, centered and muted */
.prose p {
    text-align: center;
}

/* Chat message bubbles */
.message-wrap .message {
    border-radius: 16px !important;
    padding: 12px 16px !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
    animation: fadeInUp 0.25s ease-out;
}

.message-wrap .message.user {
    background: linear-gradient(135deg, #7c3aed, #0891b2) !important;
    color: #f8fafc !important;
}

.message-wrap .message.bot {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
}

/* Chatbot panel container */
.bubble-wrap {
    background: transparent !important;
}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-thumb {
    background: #7c3aed;
    border-radius: 8px;
}
::-webkit-scrollbar-track {
    background: transparent;
}

/* Entrance animation for new messages */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Example prompt chips */
.example {
    border-radius: 999px !important;
    border: 1px solid #7c3aed !important;
    transition: all 0.15s ease-in-out;
}
.example:hover {
    background: rgba(124, 58, 237, 0.15) !important;
    transform: translateY(-1px);
}

/* Submit button glow on hover */
button.primary:hover {
    box-shadow: 0 0 20px rgba(168, 85, 247, 0.5);
}
"""


# =====================================================================
# GRADIO CHAT FUNCTION
# =====================================================================
def chat_function(message: str, history: list[dict]):
    """
    Adapter between Gradio's ChatInterface and our tool-calling loop.

    Gradio calls this on every user turn, passing the new message and
    the prior conversation history (as a list of {"role", "content"}
    dicts, matching the format our own message list already uses).

    We build a fresh message list on every call -- system prompt plus
    the existing history plus the new message -- rather than mutating
    Gradio's history directly, so the system prompt's rules are always
    freshly and consistently applied.

    This is a GENERATOR: it yields progressively longer slices of the
    final reply to create a character-by-character "typing" effect in
    the UI. The underlying tool-calling logic (get_assistant_response)
    is unchanged and still runs as a normal, fully-tested function call
    -- we're only revealing its already-correct result gradually.

    Args:
        message: The latest user message.
        history: The prior conversation, as Gradio-managed message dicts.

    Yields:
        Progressively longer prefixes of the assistant's reply text.
    """
    conversation_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    conversation_messages.extend(history)
    conversation_messages.append({"role": "user", "content": message})

    full_reply = get_assistant_response(conversation_messages)

    # Reveal the reply a few characters at a time. CHUNK_SIZE and
    # TYPING_DELAY_SECONDS control the speed -- small chunks with a
    # tiny delay feel like natural typing without dragging on.
    CHUNK_SIZE = 3
    TYPING_DELAY_SECONDS = 0.012

    revealed_text = ""
    for position in range(0, len(full_reply), CHUNK_SIZE):
        revealed_text = full_reply[: position + CHUNK_SIZE]
        yield revealed_text
        time.sleep(TYPING_DELAY_SECONDS)

    # Ensure the full reply is always the final yielded value, even if
    # the loop above was skipped (e.g., empty reply).
    yield full_reply


# =====================================================================
# LAUNCH THE GRADIO APP
# =====================================================================
def build_interface() -> gr.ChatInterface:
    """
    Build the Gradio ChatInterface for the TechStore AI Customer
    Support Assistant.

    Returns:
        A configured gr.ChatInterface, ready to be launched.
    """
    styled_chatbot = gr.Chatbot(
        avatar_images=(USER_AVATAR_PATH, BOT_AVATAR_PATH),
        elem_classes=["techstore-chatbot"],
    )

    return gr.ChatInterface(
        fn=chat_function,
        chatbot=styled_chatbot,
        fill_height=True,
        title="TechStore AI Customer Support Assistant",
        description=(
            "Ask about order status, product availability, cancellations, "
            "refund eligibility, or support tickets. If I can't resolve "
            "your issue, I'll escalate it to our human support team."
        ),
        examples=[
            "What's the status of order 1001?",
            "Do you have any laptops in stock?",
            "Can I cancel order 1003?",
            "Am I eligible for a refund on order 1003?",
        ],
    )


if __name__ == "__main__":
    interface = build_interface()
    interface.launch(share=True, theme=CUSTOM_THEME, css=CUSTOM_CSS)