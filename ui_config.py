"""
ui_config.py

UI configuration for the TechStore AI Customer Support Assistant.

This file contains:
    - UI asset paths
    - Gradio theme configuration
    - Custom CSS styling

Keeping UI configuration separate from main.py makes the application
orchestration code easier to read and maintain.
"""

import os

import gradio as gr


# =====================================================================
# UI ASSETS
# =====================================================================

ASSETS_DIR = os.path.join(
    os.path.dirname(__file__),
    "assets",
)

USER_AVATAR_PATH = os.path.join(
    ASSETS_DIR,
    "user_avatar.png",
)

BOT_AVATAR_PATH = os.path.join(
    ASSETS_DIR,
    "bot_avatar.png",
)


# =====================================================================
# GRADIO THEME
# =====================================================================

# A dark, purple/cyan-accented theme built on Gradio's base theme.
#
# The theme controls the overall visual appearance of Gradio
# components, including colors, fonts, borders, backgrounds, and
# buttons.

CUSTOM_THEME = gr.themes.Base(
    primary_hue=gr.themes.colors.purple,
    secondary_hue=gr.themes.colors.cyan,
    neutral_hue=gr.themes.colors.slate,
    font=[
        gr.themes.GoogleFont("Inter"),
        "ui-sans-serif",
        "system-ui",
        "sans-serif",
    ],
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
    button_primary_background_fill=(
        "linear-gradient(135deg, #a855f7, #22d3ee)"
    ),
    button_primary_background_fill_hover=(
        "linear-gradient(135deg, #9333ea, #06b6d4)"
    ),
    button_primary_text_color="#0f172a",
    body_text_color="#e2e8f0",
    body_text_color_dark="#e2e8f0",
    body_text_color_subdued="#94a3b8",
)


# =====================================================================
# CUSTOM CSS
# =====================================================================

CUSTOM_CSS = """
/* Lock the page to the viewport -- no page-level scrollbar.
   Only the chat panel itself is allowed to scroll internally. */
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
    background: radial-gradient(
        circle at top left,
        #1e1b4b 0%,
        #0f172a 45%
    ) !important;
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
    filter: drop-shadow(
        0 0 18px rgba(168, 85, 247, 0.35)
    );
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
    background: linear-gradient(
        135deg,
        #7c3aed,
        #0891b2
    ) !important;
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
    from {
        opacity: 0;
        transform: translateY(6px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
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