# 🏥 AI Appointment Scheduler

An end-to-end AI-powered chatbot for scheduling medical appointments.
This project demonstrates a **production-style agent architecture** using a LangGraph-inspired workflow, FastAPI backend, and Streamlit frontend.

---

## ✨ Features

* 💬 Conversational patient intake (name, DOB, insurance, complaint, address)
* 🧠 Graph-based agent orchestration (LangGraph-style execution)
* 📍 Address validation via Google Maps API
* 📅 Interactive appointment selection UI
* 💾 Persistent session memory (JSON-backed)
* ⚡ Real-time UI updates with Streamlit

---

## 🏗️ Architecture

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

## 📁 Project Structure

```text
ai_scheduler/
│
├── app.py                  # FastAPI entrypoint
├── config.py               # environment config
├── requirements.txt
├── run.sh                  # run script
│
├── graph/
│   ├── state.py
│   ├── graph.py
│   ├── nodes.py
│   ├── routers.py
│
├── services/
│   ├── llm.py
│   ├── extractor.py
│   ├── google_maps.py
│   ├── providers.py
│
├── storage/
│   ├── memory.py
│
├── schemas/
│   ├── api.py
│
└── ui.py                   # Streamlit frontend
```

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone <your-repo-url>
cd ai_scheduler
```

---

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
# OR
venv\Scripts\activate      # Windows
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Set environment variables

Create a `.env` file in the root:

```env
OPENAI_API_KEY=your_openai_api_key
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
```

> Note: If the Google Maps key is missing, address validation will fall back to a mock success.

---

## ▶️ Run the App

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

## 🧪 How It Works

1. User enters information via chat
2. Backend processes input through a **graph-based agent**
3. Agent:

   * extracts structured data
   * determines next step
   * calls tools (e.g., address validation)
4. UI updates dynamically:

   * asks next question OR
   * shows appointment buttons
5. User selects a slot → confirmation → completion

---

## 🧠 Agent Design

This project uses a **LangGraph-style state machine**, where:

* Nodes = actions (extract info, validate address, show appointments)
* Edges = transitions between steps
* State = shared memory across the conversation

This enables:

* automatic flow progression
* clean separation of logic
* easier debugging and extensibility

---

## 📌 Example Flow

```text
User → "I need to see a doctor"
 → collect patient info
 → validate address
 → show available providers
 → user selects time
 → confirm appointment
 → ✅ done
```

---

## 🔧 Technologies Used

* FastAPI
* Streamlit
* OpenAI API
* LangGraph (agent orchestration)
* Google Maps Geocoding API
* Python (stateful backend logic)

---

## 📈 Future Improvements

* Replace mock providers with real scheduling API
* Add insurance verification step
* Deploy to cloud (Render / AWS / GCP)
* Use Redis/Postgres for scalable persistence
* Add async tool execution
* Improve NLP extraction with structured LLM outputs

---

## 💼 Why This Project Matters

This project demonstrates:

* real-world AI system design
* agent orchestration patterns
* API + frontend integration
* stateful conversational UX

It is representative of modern **healthcare AI, clinical workflows, and applied ML systems**.

---

## 📝 License

MIT License
