import smtplib
from email.mime.text import MIMEText

import streamlit as st
from google import genai
from google.genai import types

from prompts import (
    SYSTEM_PROMPT,
    WELCOME_MESSAGE_TEMPLATE,
    SUMMARY_REQUEST_PROMPT,
)


MODEL_NAME = "gemini-2.5-flash"

st.set_page_config(
    page_title="MacroSnap",
    page_icon="🥗"
)

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

GMAIL_ADDRESS = st.secrets["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD = st.secrets["GMAIL_APP_PASSWORD"]


@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)


gemini_client = get_gemini_client()


# Step 1: onboarding
if "onboarded" not in st.session_state:
    st.title("🥗 MacroSnap")
    st.caption("Snap it. Track it. Email yourself the results.")

    with st.form("onboarding_form"):
        name = st.text_input("Your name")

        email_address = st.text_input(
            "Email address",
            placeholder="you@gmail.com",
            help="This is the email address MacroSnap will send your summary to.",
        )

        submitted = st.form_submit_button("Let's go 🚀")

        if submitted:
            if not name.strip() or not email_address.strip():
                st.warning("Please fill in both your name and email address.")
            else:
                st.session_state.name = name.strip()
                st.session_state.email_address = email_address.strip()

                st.session_state.chat = gemini_client.chats.create(
                    model=MODEL_NAME,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT
                    ),
                )

                st.session_state.messages = []
                st.session_state.onboarded = True
                st.rerun()

    st.stop()


# Chat interface
def render_message(message):
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.write(message["content"])
        elif message["kind"] == "image":
            st.image(message["content"])


def add_message(role, kind, content):
    st.session_state.messages.append(
        {
            "role": role,
            "kind": kind,
            "content": content,
        }
    )

    render_message(st.session_state.messages[-1])


# Gemini conversation
def ask_gemini(parts):
    try:
        return st.session_state.chat.send_message(parts).text
    except Exception as error:
        return f"Sorry, something went wrong: {error}"


# Email cleanup
def clean_email_text(text):
    if not text:
        return "No nutrition summary available."

    text = " ".join(text.split())

    return text[:1500] + "..." if len(text) > 1500 else text


# Send summary by Gmail
def send_email(to_address, subject, body):
    try:
        message = MIMEText(clean_email_text(body))
        message["Subject"] = subject
        message["From"] = GMAIL_ADDRESS
        message["To"] = to_address

        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465
        ) as server:
            server.login(
                GMAIL_ADDRESS,
                GMAIL_APP_PASSWORD
            )

            server.send_message(message)

        return True, "Email sent successfully."

    except Exception as error:
        return False, str(error)


# Header and email button
header_col, button_col = st.columns(
    [5, 2],
    vertical_alignment="center"
)

with header_col:
    st.title("🥗 MacroSnap")

with button_col:
    send_disabled = len(st.session_state.messages) <= 2

    if st.button(
        "📧 Send to Email",
        disabled=send_disabled,
        use_container_width=True
    ):
        with st.spinner("Summarizing your day..."):
            summary = ask_gemini(
                [SUMMARY_REQUEST_PROMPT]
            )

            success, info = send_email(
                st.session_state.email_address,
                "MacroSnap Nutrition Summary",
                summary
            )

        if success:
            st.success("Sent! Check your email 📧")
        else:
            st.error(f"Couldn't send the email: {info}")


st.caption(
    f"Logged in as {st.session_state.name} - "
    f"updates go to {st.session_state.email_address}"
)


# Welcome message / previous messages
if not st.session_state.messages:
    add_message(
        "assistant",
        "text",
        WELCOME_MESSAGE_TEMPLATE.format(
            name=st.session_state.name
        ),
    )
else:
    for message in st.session_state.messages:
        render_message(message)


# Text and photo input
user_input = st.chat_input(
    "Ask a question, or attach a photo of your meal",
    accept_file=True,
    file_type=["jpg", "jpeg", "png"],
)


if user_input:
    photo = user_input.files[0] if user_input.files else None
    text = user_input.text

    parts = []

    if photo is not None:
        photo_bytes = photo.getvalue()

        add_message(
            "user",
            "image",
            photo_bytes
        )

        parts.append(
            types.Part.from_bytes(
                data=photo_bytes,
                mime_type=photo.type
            )
        )

    if text:
        add_message(
            "user",
            "text",
            text
        )

        parts.append(text)

    elif photo is not None:
        parts.append(
            "What is this meal? Give me the calories and macros."
        )

    with st.spinner("Crunching the numbers..."):
        answer = ask_gemini(parts)

    add_message(
        "assistant",
        "text",
        answer
    )
