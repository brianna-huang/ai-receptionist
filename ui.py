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

if "pending_buttons" not in st.session_state:
    st.session_state.pending_buttons = None


# ---- Auto-start conversation ----
if "initialized" not in st.session_state:
    st.session_state.initialized = True

    response = requests.post(
        BACKEND_URL,
        json={
            "session_id": st.session_state.session_id,
            "message": ""
        }
    )

    data = response.json()

    st.session_state.messages.append({
        "role": "assistant",
        "content": data["message"]
    })


# ---- Display chat history ----
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ---- Render appointment buttons ----
if st.session_state.pending_buttons and not st.session_state.is_complete:
    structured_data = st.session_state.pending_buttons

    st.divider()
    st.subheader("Available Appointments")

    for provider in structured_data:
        st.subheader(f"{provider['name']} ({provider['specialty']})")

        for time in provider["times"]:
            if st.button(
                f"{provider['name']} - {time}",
                key=f"{provider['name']}_{time}"
            ):
                # Add user message
                selection_text = f"I choose {provider['name']} at {time}"
                st.session_state.messages.append({
                    "role": "user",
                    "content": selection_text
                })

                # Call backend WITH selection
                response = requests.post(
                    BACKEND_URL,
                    json={
                        "session_id": st.session_state.session_id,
                        "message": "",
                        "selection": {
                            "provider": provider["name"],
                            "time": time
                        }
                    }
                )

                data = response.json()

                # Add assistant response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": data["message"]
                })

                # Clear buttons after selection
                st.session_state.pending_buttons = None

                # Update completion
                st.session_state.is_complete = data["is_complete"]

                st.rerun()


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
                    bot_reply = data["message"]
                    structured_data = data.get("data")
                    step = data.get("step")

                    # ✅ ALWAYS show bot reply FIRST
                    st.markdown(bot_reply, unsafe_allow_html=True)

                    # Save assistant message
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": bot_reply
                    })

                    # ✅ Store buttons for NEXT render cycle
                    if step == "show_appointments" and structured_data:
                        st.session_state.pending_buttons = structured_data
                        st.rerun()
                    else:
                        st.session_state.pending_buttons = None

                    # Update completion
                    st.session_state.is_complete = data["is_complete"]

                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.markdown(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })


# ---- Sidebar ----
with st.sidebar:
    st.header("Session Info")
    st.write(f"Session ID: {st.session_state.session_id[:8]}...")

    if st.button("Reset Conversation"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.is_complete = False
        st.session_state.pending_buttons = None
        st.rerun()


# ---- Completion UI ----
if st.session_state.is_complete:
    st.success("✅ Appointment scheduled successfully!")

    if st.button("Start New Appointment"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.is_complete = False
        st.session_state.pending_buttons = None
        st.rerun()