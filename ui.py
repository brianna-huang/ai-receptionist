import streamlit as st
import requests
import uuid

# ---- Config ----
BACKEND_URL = "http://127.0.0.1:8000/chat"

st.set_page_config(page_title="AI Scheduler", page_icon="🏥")

st.title("🏥 AI Appointment Scheduler")

# ---- Session State ----
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "is_complete" not in st.session_state:
    st.session_state.is_complete = False


# ---- Display chat history ----
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ---- Chat input ----
if not st.session_state.is_complete:
    user_input = st.chat_input("Type your message...")

    if user_input:
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        with st.chat_message("user"):
            st.markdown(user_input)

        # Call backend
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = requests.post(
                        BACKEND_URL,
                        json={
                            "session_id": st.session_state.session_id,
                            "message": user_input
                        }
                    )

                    data = response.json()
                    bot_reply = data["response"]
                    st.session_state.is_complete = data["is_complete"]

                except Exception as e:
                    bot_reply = f"❌ Error: {str(e)}"

            st.markdown(bot_reply)

        # Save assistant message
        st.session_state.messages.append({
            "role": "assistant",
            "content": bot_reply
        })


# ---- Completion UI ----
if st.session_state.is_complete:
    st.success("✅ Appointment scheduled successfully!")

    if st.button("Start New Appointment"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.is_complete = False
        st.rerun()