
import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# Load the values from the .env file
load_dotenv()

# Read Azure configuration
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# Configure the web page
st.set_page_config(
    page_title="My AI Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 My AI Chatbot")
st.caption("Powered by GPT-4.1 mini on Azure AI Foundry")

# Check whether configuration is complete
if not endpoint or not api_key or not deployment:
    st.error(
        "Azure configuration is missing. "
        "Please check your .env file."
    )
    st.stop()

# Connect to the Azure deployment

client = OpenAI(
    base_url=endpoint,
    api_key=api_key
)
# Instructions that define the chatbot's behavior
SYSTEM_PROMPT = """
You are a helpful, friendly, and knowledgeable AI assistant.
Answer the user's questions clearly and accurately.
Explain difficult concepts in simple language.
Use examples when useful.
If you are unsure about something, say so honestly.
"""

# Initialize conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Clear conversation button
if st.button("Clear chat"):
    st.session_state.messages = []
    st.rerun()

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input box for the user's question
user_prompt = st.chat_input("Ask me anything...")

if user_prompt:
    # Display the user's message
    st.session_state.messages.append(
        {"role": "user", "content": user_prompt}
    )

    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Generate the assistant's response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.chat.completions.create(
                    model=deployment,
                    messages=[
                        {
                            "role": "system",
                            "content": SYSTEM_PROMPT
                        },
                        *st.session_state.messages
                    ],
                    temperature=0.7,
                    max_tokens=800
                )

                answer = response.choices[0].message.content

                if not answer:
                    answer = "The model returned an empty response."

                st.markdown(answer)

                # Save the assistant's response
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

            except Exception as error:
                st.error(
                    "Sorry, I couldn't get a response from Azure. "
                    "Check your endpoint, API key, deployment name, "
                    "and Azure deployment status."
                )
                st.caption(f"Technical details: {error}")

                # Remove the unanswered user message from history
                st.session_state.messages.pop()
