"""
ui_config.py

UI configuration for the TechStore AI Customer Support Assistant.

This file contains:
    - UI asset paths
    - Gradio theme configuration
    - Custom CSS styling (Including Voice Control layout & responsiveness)
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
    overflow-y: auto !important;
    display: flex !important;
    flex-direction: column !important;
    background: radial-gradient(
        circle at top left,
        #1e1b4b 0%,
        #0f172a 45%
    ) !important;
    padding: 16px !important;
}

.gradio-container > .main,
.gradio-container > div:first-child {
    height: 100% !important;
    min-height: 0 !important;
    display: flex !important;
    flex-direction: column !important;
}

/* Title and description stay fixed-size at the top */
h1, p {
    flex-shrink: 0 !important;
}

/* Chatbot panel grows to fill remaining space */
.techstore-chatbot {
    flex: 1 1 auto !important;
    min-height: 250px !important;
    overflow-y: auto !important;
}

/* Title styling */
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
    margin-bottom: 4px !important;
}

p {
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

.bubble-wrap {
    background: transparent !important;
}

/* Text Input & Send Row */
.input-row {
    display: flex !important;
    gap: 8px !important;
    margin-top: 10px !important;
    align-items: center !important;
}

.send-btn {
    border-radius: 12px !important;
    height: 100% !important;
}

/* Voice Input Container & Styling */
.voice-accordion {
    border: 1px solid #334155 !important;
    border-radius: 14px !important;
    background: #1e293b !important;
    margin-top: 10px !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.voice-input-row {
    gap: 16px !important;
    align-items: stretch !important;
    padding: 8px 0 !important;
}

.audio-component {
    background: #111827 !important;
    border-radius: 12px !important;
    border: 1px solid #334155 !important;
}

/* Voice & Clear Action Buttons */
.voice-btn {
    background: linear-gradient(135deg, #a855f7, #22d3ee) !important;
    color: #0f172a !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
    margin-bottom: 6px !important;
}

.clear-btn {
    background: #334155 !important;
    color: #f8fafc !important;
    border-radius: 10px !important;
    margin-bottom: 8px !important;
}

.clear-btn:hover {
    background: #475569 !important;
}

/* Status Textbox Styling */
.status-textbox textarea, .status-textbox input {
    background-color: #0f172a !important;
    color: #67e8f9 !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
    border: 1px solid #334155 !important;
    font-size: 0.85rem !important;
}

/* Custom Scrollbar */
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

/* Animations */
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

/* Responsive Layout Adjustments */
@media (max-width: 768px) {
    .voice-input-row {
        flex-direction: column !important;
    }
    .input-row {
        flex-direction: row !important;
    }
}

/* Submit button glow on hover */
button.primary:hover {
    box-shadow: 0 0 20px rgba(168, 85, 247, 0.5);
}
"""