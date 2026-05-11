# AI Appointment Scheduler

An end-to-end AI-powered chatbot for scheduling medical appointments.
This project uses a LangGraph-inspired workflow, FastAPI backend, and Streamlit frontend.

---

## Features

* Conversational patient intake (name, DOB, insurance, complaint, address)
* Graph-based agent orchestration (LangGraph-style execution)
* Address validation via Google Maps API
* Interactive appointment selection UI
* Persistent session memory (JSON-backed)
* Real-time UI updates with Streamlit

---

## Architecture

```text
Streamlit UI
   ↓
FastAPI Backend (/chat)
   ↓
LangGraph Agent
   ├── LLM (OpenAI)
   ├── Address Validation (Google Maps API)
   └── Provider Availability (mock data)
   ↓
Persistent Memory (sessions.json)
```
---

## Getting Started

### 1. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
# OR
venv\Scripts\activate      # Windows
```

---

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Set environment variables

Create a `.env` file in the root:

```env
OPENAI_API_KEY=your_openai_api_key
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
```

> Note: If the Google Maps key is missing, address validation will fall back to a mock success.

---

## Run the App

### Option 1 (recommended)

```bash
./run.sh
```

---

### Option 2 (manual)

Start backend:

```bash
uvicorn app:app --reload
```

Start frontend (in another terminal):

```bash
streamlit run ui.py
```

---

## How It Works

1. User enters information via chat
2. Backend processes input through a graph-based agent
3. Agent:
   * extracts structured data
   * determines next step
   * calls tools (e.g., address validation)
4. UI updates dynamically:
   * asks next question OR
   * shows appointment buttons
5. User selects a slot → confirmation → completion

---

## Agent Design

This project uses a LangGraph-style state machine, where:
* Nodes = actions (extract info, validate address, show appointments)
* Edges = transitions between steps
* State = shared memory across the conversation

This enables:
* automatic flow progression
* clean separation of logic
* easier debugging and extensibility

---

## Tech Stack

* FastAPI
* Streamlit
* OpenAI API
* LangGraph (agent orchestration)
* Google Maps Geocoding API
* Python (stateful backend logic)

---

## Future Improvements

* Replace mock providers with real scheduling API
* Add insurance verification step
* Deploy to cloud (Render / AWS / GCP)
* Use Postgres for scalable persistence
* Add async tool execution
* Improve NLP extraction with structured LLM outputs

## License

MIT License
