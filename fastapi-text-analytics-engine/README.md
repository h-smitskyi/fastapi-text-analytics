# 🔬 Text Analytics Engine

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A lightweight, high-performance **REST API microservice** for text analysis — built with **FastAPI** and raw algorithmic implementations. No external NLP libraries; every operation is powered by carefully chosen data structures to demonstrate **algorithmic efficiency** and **clean architecture**.

---

## ✨ Features

| Capability | Implementation |
|---|---|
| **Word Frequency Counting** | Hash Map (`collections.Counter`) — O(1) per lookup |
| **Top-K Keywords** | Min-Heap (`heapq.nlargest`) — O(N log K) |
| **Stop-Word Filtering** | `frozenset` membership test — O(1) |
| **Text Metrics** | Character / word / sentence count, average word length |
| **Async & Thread-Safe** | `asyncio.to_thread` offloads CPU-bound work |
| **Strict Validation** | Pydantic v2 request / response models |

---

## 📁 Project Structure

```
fastapi-text-analytics-engine/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app initialisation & middleware
│   ├── api/
│   │   ├── __init__.py
│   │   └── endpoints.py     # Route definitions (controller layer)
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic request / response models
│   └── services/
│       ├── __init__.py
│       └── analyzer.py      # Core algorithmic business logic
├── Dockerfile
├── .dockerignore
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **pip** (or Docker)

### Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/fastapi-text-analytics-engine.git
cd fastapi-text-analytics-engine

# 2. Create & activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The interactive API docs are available at **http://localhost:8000/docs**.

### Docker Setup

```bash
# Build the image
docker build -t text-analytics-engine .

# Run the container
docker run -d -p 8000:8000 --name text-analytics text-analytics-engine
```

---

## 📡 API Reference

### Health Check

```
GET /health
```

```json
{ "status": "healthy" }
```

### Analyze Text

```
POST /api/v1/analyze-text
Content-Type: application/json
```

#### Request Body

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `text` | `string` | ✅ | — | Raw text to analyse (1 – 1 000 000 chars) |
| `top_n` | `int` | ❌ | `10` | Number of top keywords to return (1 – 100) |

#### cURL Example

```bash
curl -X POST http://localhost:8000/api/v1/analyze-text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The quick brown fox jumps over the lazy dog. The dog barked back at the fox. The fox ran away quickly.",
    "top_n": 5
  }'
```

#### Python `requests` Example

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/analyze-text",
    json={
        "text": "The quick brown fox jumps over the lazy dog. "
                "The dog barked back at the fox. The fox ran away quickly.",
        "top_n": 5,
    },
)
print(response.json())
```

#### Response

```json
{
  "metrics": {
    "character_count": 99,
    "word_count": 21,
    "sentence_count": 3,
    "average_word_length": 3.67
  },
  "top_words": [
    { "word": "fox", "count": 3 },
    { "word": "dog", "count": 2 },
    { "word": "quick", "count": 1 },
    { "word": "brown", "count": 1 },
    { "word": "jumps", "count": 1 }
  ],
  "word_frequencies": {
    "quick": 1,
    "brown": 1,
    "fox": 3,
    "jumps": 1,
    "lazy": 1,
    "dog": 2,
    "barked": 1,
    "back": 1,
    "ran": 1,
    "away": 1,
    "quickly": 1
  }
}
```

---

## 🧠 Technical Decisions

### Why FastAPI?

FastAPI was chosen for its **async-first design**, automatic OpenAPI documentation, and native **Pydantic** integration. It delivers high throughput under concurrent load — crucial for a text-processing microservice — while keeping the codebase lean and type-safe.

### Algorithmic Choices

| Decision | Rationale |
|---|---|
| **Hash Map for frequency counting** (`collections.Counter`) | Provides **O(1)** amortised insert and lookup. A single O(N) pass builds the complete frequency table — no secondary data structures required. |
| **Min-Heap for Top-K extraction** (`heapq.nlargest`) | Extracts the K most frequent words in **O(N log K)** time. This is strictly superior to a naïve full-sort approach (O(N log N)) when K ≪ N, and uses only O(K) auxiliary memory. |
| **`frozenset` for stop words** | Immutable hash-set guarantees **O(1)** membership checks and is allocated once at module import time — zero per-request overhead. |
| **`str.translate` for punctuation stripping** | Runs at C speed inside CPython, outperforming regex-based alternatives for simple character removal. |
| **`asyncio.to_thread`** | Offloads the synchronous, CPU-bound analysis to the default thread pool, keeping the async event loop responsive for concurrent HTTP requests. |

### Architecture

The project follows a **three-layer clean architecture**:

1. **API Layer** (`endpoints.py`) — thin controller; validates input, delegates to services, returns typed responses.
2. **Service Layer** (`analyzer.py`) — pure business logic with no framework coupling; fully unit-testable.
3. **Schema Layer** (`schemas.py`) — Pydantic models enforce contracts at the API boundary.

---

## 📄 License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).
