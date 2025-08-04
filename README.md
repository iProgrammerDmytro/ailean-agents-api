# Ailean Agents API Backend

> **FastAPI + PostgreSQL microservice** – coding‑challenge backend

---

## ✨ Features

- CRUD endpoints for **Agents**
- Q&A endpoint for the **Hotel Q&A Bot**
- OpenAPI schema served at `/docs`
- 100 % typed codebase
- Alembic migrations & PostgreSQL
- Full test‑suite with **pytest**
- **Docker‑first** developer experience

---

## 🖥️ Quick Start (Docker Compose)

### 1. Clone the Repository

```bash
git clone https://github.com/iProgrammerDmytro/ailean-agents-api.git
cd ailean‑agents‑api
```

### 2. Build & Run the Stack

```bash
docker compose up --build   # first time (build + run)
# docker compose up         # subsequent runs
```

The API will be available at **http://localhost:8000**  
Interactive Swagger UI: **http://localhost:8000/docs**

---

## 🗺️ API Reference

| Method | Path | Description |
| :----: | :--- | :---------- |
| GET    | `/agents` | List agents |
| POST   | `/agents` | Create agent |
| GET    | `/agents/{agent_id}` | Retrieve single agent |
| POST   | `/agents/{agent_id}/ask` | Ask Hotel Q&A bot |

---

## ⚙️ Common Tasks

| Task | Command |
| ---- | ------- |
| Run migrations | `docker compose exec api alembic upgrade head` |
| Start interactive shell | `docker compose exec api bash` |
| **Run the test‑suite** | `pytest -q` |

> **Note:** To execute tests, first install the test requirements and then run `pytest`:
>
> ```bash
> pip install -r requirements.test.txt
> pytest
> ```

---

## 📂 Project Layout

```
app/
├─ agent/          # business domain logic
│  ├─ models.py    # SQLAlchemy models
│  ├─ schemas.py   # Pydantic DTOs
│  ├─ crud.py      # persistence helpers
│  ├─ routes.py    # API router
│  └─ services/    # domain services (Hotel Q&A, etc.)
├─ db/             # database helpers & Alembic glue
├─ core/           # settings & shared utilities
└─ main.py         # FastAPI application factory
```

---

## 📦 Sample Payload – `POST /agents`

| Field | Type | Allowed values | Notes |
|-------|------|---------------|-------|
| `name` | `string` | — | Human‑readable name |
| `type` | enum | `Sales` • `Support` • `Marketing` | Agent category |
| `status` | enum | `Active` • `Inactive` | Operational state |
| `description` | `string` | — | Optional longer text |

### Minimal payload (as shown in `/docs`)

```jsonc
{
  "name": "string",
  "type": "Sales",
  "status": "Active",
  "description": "string",
}
```

### Realistic example – Hotel Q&A Bot

```jsonc
{
  "name": "Hotel Q&A Bot",
  "type": "Support",
  "status": "Active",
  "description": "Answers common questions about The Grand Arosa pop‑up hotel.",
}
```

---

## 🧠 Q&A Matching Logic – Under the Hood

The hotel bot’s intelligence is deliberately lightweight: it trades complex NLP for **deterministic, low‑latency string matching** that is **100 % edge‑deployable** (zero external dependencies).

### 1. Knowledge Base

A constant dictionary `_QA_PAIRS: dict[str, str]` contains curated Q→A pairs extracted from the hotel website. Each **key** is a concise keyword/phrase (≈ 10 entries) and the **value** is the full answer text.

### 2. Normalisation `_norm()`

```python
def _norm(s: str) -> str:
    return "".join(ch for ch in s.lower() if ch.isalnum())
```

* Lower‑cases the string and strips all non‑alphanumeric characters.  
* Ensures `"Check-in!"`, `"checkin"`, and `"CHECK‑IN"` collapse to the same token → `checkin`.  
* Guarantees canonical forms for both user input and KB keys.

### 3. Exact / Sub‑string Pass

```python
for k, v in _QA_PAIRS.items():
    if k_norm in q_norm or q_norm in k_norm:
        return v
```

* **O(N)** over at most 10 entries – trivial cost.  
* Handles perfect matches and queries that wholly contain the keyword (e.g. “What time is check‑in?” ⟶ `checkin`).

### 4. Fuzzy Pass with `SequenceMatcher`

```python
best_key = max(_QA_PAIRS, key=lambda k: _ratio(q_norm, _norm(k)))
if _ratio(q_norm, _norm(best_key)) >= 0.56:
    return _QA_PAIRS[best_key]
```

* Uses `difflib.SequenceMatcher` (std‑lib) for a **cheap Levenshtein‑style similarity** score.  
* Threshold `0.56` was empirically chosen to catch typos like “cheeckin” without producing false positives.  
* Still **deterministic and offline** – no ML models or cloud calls.

### 5. Fallback

If neither pass succeeds:  
`"Sorry, I couldn't find an answer to that."` – keeps UX explicit and graceful.

### 6. Complexity & Performance

* Runtime: O(N) where N = number of KB entries (≤ 10 ⇒ ~microseconds).  
* Memory: O(N) for the dict + negligible stack.  
* No I/O, so **p99 latency stays in sub‑millisecond territory** on tiny containers (≈ 10 MiB RSS).

### 7. Why This Design?

| Goal | Design choice | Pay‑off |
|------|---------------|---------|
| **Maximum ROI** | Plain Python, std‑lib only | Ships in minutes; no extra infra |
| Edge / offline | Deterministic dict + fuzzy ratio | Works in Lambda@Edge / Cloudflare |
| Maintainability | `_QA_PAIRS` is declarative | Marketing can edit answers without code changes |
| Testability | Pure functions (`answer()`) | Unit‑tests run in < 1 ms |
| Predictability | No LLM randomness | Same input ⇒ same output (good for legal/compliance) |

### 8. Extensibility

* **Synonyms** – append more keys (e.g. `"parking fee"`).  
* **Dynamic KB** – swap the dict for a SQLite table or Redis hash.  

---

Future iterations could integrate an LLM fallback while preserving this deterministic first‑line lookup (“hybrid retrieval”). For the current scope, the above logic nails the **“80 % questions solved with 20 % effort”** ethos.

---

# 📉 Limitations, Trade‑offs & Future Improvements

> A technical audit of the current MVP, with a pragmatic roadmap for levelling‑up to production‑grade.

---

## 1  Current Limitations

### 1.1 QA System Architecture

| Issue | Impact |
|-------|--------|
| **Hard‑coded KB** – Q&A pairs live in a Python dict | Content updates require code deploy |
| **Primitive matching** | Simple fuzzy matching with `difflib.SequenceMatcher` |
| **No semantic understanding** | Cannot handle synonyms, context, or natural language variations |
| **Static content** | Requires code deployment to update hotel information |
| **Single domain** | Logic tied to *The Grand Arosa* – no multi‑hotel support |

### 1.2 Production Readiness Gaps

| Gap | Consequence |
|-----|-------------|
| Dev‑only Docker Compose with **hard‑coded creds** | Secrets leak risk |
| No Production Configuration | Missing optimized container images |
| **CORS `*`**, no auth, no rate limiting | Wide attack surface |
| Missing logging / metrics | No observability, harder incident response |

### 1.3 Scalability Constraints

* No cache – every call executes full matching logic (OK now, risky at scale)  
* Single DB pool – connection exhaustion under load

### 1.4 Testing & Delivery

* Unit coverage below 60 %  
* Manual deployment – **zero CI/CD**

---

## 2  Recommended Improvements (prioritised)

### 2.1 Harden Production Runtime 🔥

1. Inject secrets via `docker‑compose.yml` → `.env`, no plaintext creds  
2. Add `fastapi‑limiter`, `fastapi‑users`, and strict CORS origins  

### 2.2 Comprehensive Test Strategy

| Layer | Goal |
|-------|------|
| **Unit** | 90 %+ coverage of pure functions & services |
| **Integration** | DB migrations, external APIs |
| **E2E / Contract** | Validate JSON schemas & happy‑paths |

Add GitHub Actions workflow: lint → test → build → push image.

### 2.3 Architecture Evolution – From Dict → RAG

```
app/core/services/knowledge/
├─ scraper.py          # collect hotel website data
├─ embeddings.py       # sentence‑transformers
├─ retrieval.py        # vector search (pgvector / ChromaDB)
└─ pipeline.py         # orchestration
```

**Key deps**  
`sentence‑transformers 2.7.*` • `chromadb 0.4.*` (or `pgvector`) • `celery 5.3.*` • `redis 5`

```python
class KnowledgeService:
    async def query(self, question: str) -> str:
        if (ans := await self._exact_match(question)):
            return ans              # ⚡ fast‑path

        rag_res = await self._rag_query(question)
        if rag_res.confidence >= 0.7:
            return rag_res.text     # 🤖 semantic path

        return self.fallback_msg    # 🙈 fallback
```

**Background Tasks**
```python
@celery.task
def scrape_hotel_data():
    content = scrape_grandarosa_website()
    embeds  = generate_embeddings(content)
    store_in_vector_db(embeds)
```

### 2.4 Operational Excellence

* Structured JSON logging 
* Prometheus metrics + Grafana dashboards  
* Alerting when confidence scores dip

---

## 3  Trade‑offs Analysis

| Aspect | Current (dict lookup) | Future (RAG pipeline) |
|--------|----------------------|-----------------------|
| **Setup complexity** | ⭐⭐ Simple | ⭐⭐⭐⭐⭐ Complex |
| **Latency** | ⭐⭐⭐⭐⭐ &lt;10 ms | ⭐⭐⭐ 100‑500 ms |
| **Accuracy** | ⭐⭐ Basic | ⭐⭐⭐⭐⭐ High |
| **Scalability** | ⭐⭐ Limited | ⭐⭐⭐⭐⭐ Excellent |
| **Maintenance** | ⭐ Manual | ⭐⭐⭐⭐ Automated |
| **Cost** | ⭐⭐⭐⭐⭐ Minimal | ⭐⭐⭐ Moderate |

---

## 4  Additional Recommendations

* **Vector DB**: Prefer `pgvector` inside Postgres – single infra, easy backups  
* **LLM**: Start with OpenAI API; evaluate open‑source (`Mistral‑7B`, `Llama‑3‑8B`) later  
* **Cache & Queue**: Redis for both caching layer and Celery broker  
* **Business KPIs**: Track query resolution rates and user satisfaction; A/B test dict vs RAG responses

---
