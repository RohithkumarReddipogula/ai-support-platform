# Enterprise Customer Support Multi-Agent System

A multi-agent AI system built for the Band of Agents Hackathon 2026. Four specialised agents collaborate through the Band platform to automatically handle customer support tickets from initial triage through to final response approval.

## What it does

When a customer submits a support ticket, the system routes it through four agents in sequence:

1. The Triage Agent reads the ticket, classifies its urgency (HIGH, MEDIUM, or LOW) and topic (BILLING, ACCESS, TECHNICAL, or GENERAL), then hands off to the Knowledge Agent.

2. The Knowledge Agent searches a hybrid retrieval knowledge base using BM25 sparse search fused with Microsoft E5-base-v2 dense embeddings. The fusion weight alpha=0.70 was discovered through systematic experimentation during MSc thesis research and validated with a paired t-test at p=0.002, achieving 93% Recall@10 on 8.84 million MS MARCO passages.

3. The Resolution Agent receives the retrieved knowledge and drafts a professional response. If the retrieval confidence score falls below 0.4, it flags the ticket for escalation instead of drafting a response.

4. The Review Agent performs a final quality check on the drafted response. It approves responses that pass the confidence threshold and escalates to human review for anything that does not meet the quality bar.

All four agents communicate through Band chat rooms using the Band SDK and LangGraph adapters.

## Demo

Live demo of agents running on Band platform:

- Band platform: https://app.band.ai
- YouTube walkthrough: [Insert your YouTube link here]

## Architecture

```
Customer Ticket
      |
      v
[Triage Agent]
 - Classifies urgency and topic
 - Routes to Knowledge Agent
      |
      v
[Knowledge Agent]
 - Hybrid RAG: BM25 + E5-base-v2 dense embeddings
 - Fusion weight alpha=0.70 (validated p=0.002)
 - Returns top 3 results with confidence score
      |
      v
[Resolution Agent]
 - Drafts customer response
 - Flags low-confidence tickets for escalation
      |
      v
[Review Agent]
 - Quality check and approval gate
 - Approves or escalates to human review
      |
      v
Approved Response
```

## Track

Track 1: Internal Enterprise Workflows

## Tech Stack

- Band SDK 1.0.0 with LangGraph adapter
- Groq API (llama-3.1-8b-instant) as the LLM provider
- LangChain and LangGraph for agent orchestration
- FAISS for vector indexing
- BM25 (rank-bm25) for sparse retrieval
- sentence-transformers (all-MiniLM-L6-v2) for dense embeddings
- Python 3.11

## Key Research Finding

The Knowledge Agent uses a hybrid retrieval approach where the optimal fusion weight between sparse and dense retrieval is alpha=0.70, not the commonly assumed 0.50. This was the central finding of my MSc thesis in Data Science, validated through 11 systematic MLflow experiments with statistical significance at p=0.002, t(99)=3.14. The system achieves 93% Recall@10, MRR=1.0, at 710ms latency with a 4.46MB FAISS index on 8.84 million passages.

## Setup

### Prerequisites

- Python 3.11
- uv package manager
- Band account at band.ai
- Groq API key (free at console.groq.com)

### Installation

```bash
git clone https://github.com/RohithkumarReddipogula/rag-agent-berlin.git
cd rag-agent-berlin
uv venv
.venv\Scripts\activate
uv add "band-sdk[langgraph]" langchain-groq langchain langgraph faiss-cpu sentence-transformers rank-bm25
```

### Configuration

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

Create an `agent_config.yaml` file with your Band agent credentials:

```yaml
triage_agent:
  agent_id: "your-triage-agent-uuid"
  api_key: "your-triage-agent-api-key"

knowledge_agent:
  agent_id: "your-knowledge-agent-uuid"
  api_key: "your-knowledge-agent-api-key"

resolution_agent:
  agent_id: "your-resolution-agent-uuid"
  api_key: "your-resolution-agent-api-key"

review_agent:
  agent_id: "your-review-agent-uuid"
  api_key: "your-review-agent-api-key"
```

### Running the agents

Open four terminal windows and run one agent in each:

```bash
uv run python triage_agent.py
uv run python knowledge_agent.py
uv run python resolution_agent.py
uv run python review_agent.py
```

Once all four agents show "Agent started", go to your Band chat room and send a message mentioning @Triage Agent with a support ticket.

### Testing

Send this message in your Band chat room:

```
@Triage Agent my payment is failing and I cannot login to my account. This is urgent.
```

Watch the four agents collaborate to classify, search, draft, and approve a response in real time.

## Project Structure

```
rag-agent-berlin/
├── triage_agent.py       # Ticket classification and routing
├── knowledge_agent.py    # Hybrid RAG retrieval (BM25 + dense)
├── resolution_agent.py   # Response drafting with confidence scoring
├── review_agent.py       # Quality check and escalation gate
├── agent_config.yaml     # Band agent credentials (not committed)
├── requirements.txt      # Python dependencies
└── README.md
```

## About

Built solo by Rohith Kumar Reddipogula for the Band of Agents Hackathon, June 2026.

MSc Data Science, University of Europe for Applied Sciences, Potsdam, Germany.

- Portfolio: https://rohithkumarreddipogula.github.io
- GitHub: https://github.com/RohithkumarReddipogula
- LinkedIn: https://linkedin.com/in/rohith-kumar-reddipogula-a6692030b
- Email: rohithkumar336699@gmail.com
