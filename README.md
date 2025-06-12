# OSINT AI Agent 🤖

An AI-powered OSINT (Open Source Intelligence) investigation platform that automates the discovery, analysis, and synthesis of public information about entities (e.g., people, companies). Built using LangGraph, Gemini, Claude, and GPT-4o.

---

## ✨ Features

- ⚙️ Modular multi-agent architecture via LangGraph
- 🔍 Web-based entity investigation (LinkedIn, Google Scholar, GitHub, etc.)
- 📊 Entity relationship mapping via `spacy` + `networkx`
- 🤔 Risk scoring using Claude Opus 4 as LLM judge
- 📊 Retrieval quality scoring (confidence + decay)
- 🔀 Deduplication and citation clustering
- ⚖️ Custom model selection for retrieval/synthesis
- 📱 Responsive UI with step-wise progress feedback
- ⌚ Latency tracking (planned)

---

## 📅 Architecture

```text
            +--------------------------+
            |   User Query Submission |
            +--------------------------+
                        |
                        v
+------------> LangGraph Workflow +------------+
|              |        |                     |
|              v        v                     v
|     Query Parser  -> Task Planner     -> Retriever (GPT-4o)
|                                         |
|                                         v
|                             Web Search + Scoring + Citations
|                                         |
|                                         v
|                        Deduplication + Graph Builder (spaCy)
|                                         |
|                                         v
|                              Synthesis (Gemini, Claude)
|                                         |
|                                         v
|                             Judgement Agent (Claude Opus 4)
|                                         |
+----------------------> Final Report + Risk Score
```

---

## 🚀 Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/your-username/osint-ai-agent.git
cd osint-ai-agent
```

### 2. Backend (FastAPI)

```bash
cd backend
python -m venv osintenv
osintenv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

Create a `.env` file:

```
OPENAI_API_KEY=your-openai-key
GEMINI_API_KEY=your-gemini-key
ANTHROPIC_API_KEY=your-anthropic-key
```

Then run the backend server:

```bash
cd src
uvicorn agent.api_server:app --reload
```

### 3. Frontend (React + Vite + Tailwind)

```bash
cd frontend
npm install
npm run dev
```

- Backend: [http://localhost:8000](http://localhost:8000)
- Frontend: [http://localhost:5173](http://localhost:5173)

---

## 📂 File Structure

```text
osint-ai-agent/
├── backend/
│   ├── src/
│   │   ├── agent/               # LangGraph + agents
│   │   ├── api_server.py        # FastAPI app
│   │   └── state.py             # OSINTState definition
├── frontend/
│   ├── src/
│   │   ├── components/          # UI components
│   │   └── App.tsx              # Main React app
└── README.md
```

---

## ⚖️ Model Selection

You can choose the following models from the frontend:

### Retriever Models:

- `gpt-4o-mini-search-preview` (Fastest)
- `gpt-4o` (High quality, slower)

### Synthesis Models:

- `gemini-1.5-pro` (Balanced, fast)
- `gemini-2.0-flash` (Faster)
- `claude-opus-4-20250514` (Deepest reasoning, slowest)

Models are passed via JSON:

```json
{
  "query": "Investigate Elon Musk",
  "retrieval_model": "gpt-4o",
  "synthesis_model": "gemini-1.5-pro"
}
```

---

## 🔍 How to Use

1. Open [http://localhost:5173](http://localhost:5173)
2. Type your query (e.g., "Investigate Ali Khaledi Nasab")
3. Choose your models (optional)
4. Click **Generate OSINT Report**
5. Watch the pipeline progress in real-time!

---

## 🎉 Future Enhancements

- Add latency benchmarks (per-step duration stats)
- Chart view for credibility scores (radar or bar)
- Graph visualization of sources on the frontend using react-force-graph
- Export final report to PDF or Markdown
- Memory persistence

---

## 💏 Credits

- [LangGraph](https://github.com/langchain-ai/langgraph)
- [OpenAI Web Search Tool](https://platform.openai.com/docs/guides/tools-web-search?api-mode=responses)
- [Gemini Grounding API](https://ai.google.dev/gemini-api/docs/grounding?lang=python)
- [Anthropic Web Tool](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/web-search-tool)

---

## 🔗 GitHub

Once published, update this section:

```
https://github.com/aqibalvi/osint-ai-agent
```

---

## ✨ Demo Screenshots (Optional)

Upload these to `/frontend/public/screenshots/`:

- Entity Search Page
- StepLoader Progress
- Final Report + Graph + Citations

