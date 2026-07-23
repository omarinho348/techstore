"""
main.py

Orchestration and UI layer for the TechStore AI Customer Support
Assistant using the OpenAI Agents SDK and faster-whisper for local speech-to-text.

Architecture:

    Gradio UI (Text + Voice Input)
        |
        v
    Triage Agent
        |
        +-------------------+-------------------+
        |                   |                   |
        v                   v                   v
    Order & Product     Support Agent     Knowledge Agent
        |                   |                   |
        v                   v                   v
      Tools               Tools               Tool

Agent definitions and handoffs live in agent_team.py.
Business logic lives in tools.py.
RAG functionality lives in rag.py.
UI theme, CSS, and assets live in ui_config.py.
"""

import asyncio
import logging
import os
import time
from datetime import date

import gradio as gr
from agents import Runner
from dotenv import load_dotenv
from faster_whisper import WhisperModel

from agent_team import triage_agent
from ui_config import (
    BOT_AVATAR_PATH,
    CUSTOM_CSS,
    CUSTOM_THEME,
    USER_AVATAR_PATH,
)


# =====================================================================
# LOGGING
# =====================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# =====================================================================
# ENVIRONMENT SETUP & FASTER-WHISPER INITIALIZATION
# =====================================================================

load_dotenv()

OPENAI_API_KEY_ENV = "OPENAI_API_KEY"


def validate_environment() -> None:
    """
    Validate that the required environment variables are available.
    """
    api_key = os.environ.get(OPENAI_API_KEY_ENV)

    if not api_key:
        raise ValueError(
            f"{OPENAI_API_KEY_ENV} is not set. "
            "Add it to your .env file before running this application."
        )


validate_environment()

# Initialize local Whisper Model ("base" model running on CPU with int8 quantization)
logger.info("Loading local faster-whisper model ('base')...")
local_whisper = WhisperModel("base", device="cpu", compute_type="int8")
logger.info("Local faster-whisper model loaded successfully.")


# =====================================================================
# DATE CONTEXT
# =====================================================================

def build_date_context() -> str:
    """
    Build a short context string containing today's actual date.
    """
    today_str = date.today().strftime("%A, %B %d, %Y")
    return f"Today's date is {today_str}."


# =====================================================================
# AGENT WORKFLOW LOGGING
# =====================================================================

def log_agent_workflow(result) -> None:
    """
    Print a concise summary of the agents involved in the current run.
    """
    agents_used = []

    for item in result.new_items:
        agent = getattr(item, "agent", None)

        if agent and agent.name not in agents_used:
            agents_used.append(agent.name)

    if agents_used:
        print(f"[AGENT WORKFLOW] {' -> '.join(agents_used)}")


# =====================================================================
# AGENT RUNNER
# =====================================================================

async def run_agent_team(
    user_message: str,
    history: list[dict],
) -> str:
    """
    Run one turn through the multi-agent TechStore support team.
    """
    input_items = []

    for message in history:
        role = message.get("role")
        content = message.get("content")

        if role and content:
            input_items.append({"role": role, "content": content})

    current_user_input = (
        f"{build_date_context()}\n\n"
        f"Customer's latest message:\n"
        f"{user_message}"
    )

    input_items.append({"role": "user", "content": current_user_input})

    result = await Runner.run(
        triage_agent,
        input=input_items,
    )

    log_agent_workflow(result)

    if result.final_output is None:
        return (
            "I'm sorry, but I wasn't able to generate "
            "a response right now. Please try again."
        )

    return str(result.final_output)


# =====================================================================
# SYNCHRONOUS ADAPTER
# =====================================================================

def get_assistant_response(
    user_message: str,
    history: list[dict],
) -> str:
    """
    Bridge the synchronous Gradio function with the asynchronous
    Agents SDK runner.
    """
    return asyncio.run(
        run_agent_team(
            user_message=user_message,
            history=history,
        )
    )


# =====================================================================
# VOICE TRANSCRIPTION FUNCTIONS (LOCAL FASTER-WHISPER)
# =====================================================================

def transcribe_audio(audio_path: str) -> tuple[str, str]:
    """
    Transcribe audio recorded from the user's microphone using faster-whisper locally.

    Args:
        audio_path: Path to the recorded audio file provided by Gradio.

    Returns:
        A tuple of (transcribed_text, status_message)
    """
    if not audio_path:
        return "", "⚠️ No audio recorded. Please record audio first."

    try:
        logger.info("Transcribing audio file locally with faster-whisper: %s", audio_path)

        segments, _ = local_whisper.transcribe(audio_path, beam_size=5)
        transcribed_text = " ".join([segment.text for segment in segments]).strip()

        if not transcribed_text:
            return "", "⚠️ Transcription completed, but no speech was recognized."

        return transcribed_text, "✓ Transcription successful!"

    except Exception as error:
        logger.exception("Local voice transcription failed: %s", error)
        return "", f"❌ Transcription error: {str(error)}"


def handle_voice_input(audio_path: str) -> tuple[str, str]:
    """
    Wrapper function connecting the audio input component to transcription.
    """
    return transcribe_audio(audio_path)


# =====================================================================
# GRADIO INTERFACE BUILDER
# =====================================================================

def build_interface() -> gr.Blocks:
    """
    Build the Gradio UI using Blocks layout to support separate text input,
    send button, audio recording, transcription feedback, and custom styling.
    """
    with gr.Blocks(title="TechStore AI Support") as demo:

        gr.Markdown("# TechStore AI Customer Support Assistant")
        gr.Markdown(
            "Ask about order status, product availability, cancellations, "
            "refund eligibility, or support tickets. If I can't resolve your issue, "
            "I'll escalate it to our human support team."
        )

        # Chatbot panel
        chatbot = gr.Chatbot(
            avatar_images=(
                USER_AVATAR_PATH,
                BOT_AVATAR_PATH,
            ),
            elem_classes=[
                "techstore-chatbot",
            ],
        )

        # Chat Input Row: Textbox & Send Button
        with gr.Row(elem_classes=["input-row"]):
            msg_input = gr.Textbox(
                placeholder="Type your message or use voice input below...",
                show_label=False,
                scale=5,
                container=False,
                autofocus=True,
            )
            send_btn = gr.Button("Send", variant="primary", scale=1, elem_classes=["send-btn"])

        # Voice Input Section
        with gr.Accordion("🎙️ Voice Input (Microphone)", open=False, elem_classes=["voice-accordion"]):
            with gr.Row(elem_classes=["voice-input-row"]):
                audio_input = gr.Audio(
                    sources=["microphone"],
                    type="filepath",
                    label="Record Voice Message",
                    elem_classes=["audio-component"],
                )

                with gr.Column(scale=1):
                    transcribe_btn = gr.Button("✨ Transcribe Audio", variant="primary", elem_classes=["voice-btn"])
                    clear_audio_btn = gr.Button("🗑️ Clear Audio", elem_classes=["clear-btn"])

                    status_box = gr.Textbox(
                        label="Status",
                        interactive=False,
                        elem_classes=["status-textbox"],
                        placeholder="Awaiting audio recording...",
                    )

        # Example Prompts
        gr.Examples(
            examples=[
                "What's the status of order 1001?",
                "Do you have any laptops in stock?",
                "What is your return policy?",
                "Am I eligible for a refund on order 1003?",
            ],
            inputs=msg_input,
            label="Try an example:",
        )

        # -------------------------------------------------------------
        # EVENT HANDLERS
        # -------------------------------------------------------------

        def user_submit(user_message: str, history: list[dict]):
            """
            Append user message to chatbot and clear input field.
            """
            if not user_message or not user_message.strip():
                return "", history

            updated_history = (history or []) + [{"role": "user", "content": user_message.strip()}]
            return "", updated_history

        def bot_respond(history: list[dict]):
            """
            Generate agent response and yield word-by-word streaming effect.
            """
            if not history:
                yield history
                return

            latest_user_message = history[-1]["content"]
            chat_history = history[:-1]

            try:
                full_reply = get_assistant_response(
                    user_message=latest_user_message,
                    history=chat_history,
                )
            except Exception as error:
                logger.exception("Agent team execution failed: %s", error)
                full_reply = (
                    "I'm sorry, but I encountered an error "
                    "while processing your request. Please try again."
                )

            # Append empty bot response to stream into
            history.append({"role": "assistant", "content": ""})

            CHUNK_SIZE = 3
            TYPING_DELAY_SECONDS = 0.012

            for position in range(0, len(full_reply), CHUNK_SIZE):
                revealed_text = full_reply[: position + CHUNK_SIZE]
                history[-1]["content"] = revealed_text
                yield history
                time.sleep(TYPING_DELAY_SECONDS)

            history[-1]["content"] = full_reply
            yield history

        # Text input send events
        msg_input.submit(
            fn=user_submit,
            inputs=[msg_input, chatbot],
            outputs=[msg_input, chatbot],
            queue=False,
        ).then(
            fn=bot_respond,
            inputs=[chatbot],
            outputs=[chatbot],
        )

        send_btn.click(
            fn=user_submit,
            inputs=[msg_input, chatbot],
            outputs=[msg_input, chatbot],
            queue=False,
        ).then(
            fn=bot_respond,
            inputs=[chatbot],
            outputs=[chatbot],
        )

        # Voice input events
        transcribe_btn.click(
            fn=handle_voice_input,
            inputs=[audio_input],
            outputs=[msg_input, status_box],
        )

        clear_audio_btn.click(
            fn=lambda: (None, ""),
            inputs=None,
            outputs=[audio_input, status_box],
        )

    return demo


# =====================================================================
# APPLICATION ENTRY POINT
# =====================================================================

if __name__ == "__main__":

    logger.info("Starting TechStore AI Customer Support.")
    logger.info("Agentic architecture enabled.")
    logger.info("Starting agent: %s", triage_agent.name)

    interface = build_interface()

    interface.launch(
        share=True,
        theme=CUSTOM_THEME,
        css=CUSTOM_CSS,
    )