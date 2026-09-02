# AGENTS.md

Guidance for AI coding agents working in this repository.

This is an AI-powered insurance claims assistant. A FastAPI backend (`backend/`)
sends an uploaded accident photo to a Bedrock vision model for a damage description,
then a LangGraph agent (`backend/insurance_agent.py`) retrieves relevant policy
guidelines via MongoDB Atlas Vector Search and writes a claim summary back to MongoDB.
A Next.js frontend (`frontend/`) uploads the photo and displays the resulting claim.

## Build and test commands

Backend, from the repo root:

```sh
make poetry_start      # cd backend && poetry config virtualenvs.in-project true
make poetry_install     # cd backend && poetry install --no-interaction -v --no-cache --no-root
cd backend && poetry run uvicorn main:app --host 0.0.0.0 --port 8080
```

One-time MongoDB setup (from `backend`, after `poetry install`), before the API can
answer with real guidelines:

```sh
poetry run python scripts/create_vector_search_index.py   # creates the description_index vector index (Atlas only)
poetry run python scripts/seed_policy_documents.py         # seeds policy_documents; skipped if already seeded (idempotent)
```

Frontend, from `frontend/`:

```sh
npm install
npm run dev     # next dev -p 3000
npm run build   # next build
npm run start   # next start -H 0.0.0.0 -p 3000
```

Full stack via Docker Compose, from the repo root:

```sh
make build   # docker-compose up --build -d
make start   # docker-compose start
make stop    # docker-compose stop
make clean   # docker-compose down --rmi all -v
```

**There is no automated test suite in this repository.** No `pytest`/`npm test`
configuration exists in `backend/pyproject.toml` or `frontend/package.json`. To verify
a change, run the backend and frontend locally (or `make build && make start`), then
exercise the affected flow. Do not claim tests pass — there are none.

Smoke check after a change:

1. Start the backend (`poetry run uvicorn main:app --host 0.0.0.0 --port 8080`) and the
   frontend (`npm run dev`).
2. Upload a photo from `backend/test_photos/` through the frontend UI at
   `http://localhost:3000`.
3. Confirm streamed damage text appears (`POST /imageDescriptor`), then trigger the
   agent (`POST /runAgent`) and confirm a claim document with `date`, `description`,
   `recommendation`, and `claim_handler` fields is returned.

## Project structure

```
backend/
  main.py                     FastAPI app: /imageDescriptor and /runAgent routes
  pic2textApi.py               Streams an image to a Bedrock vision model, yields text chunks
  pic2text.py                  Non-streaming variant / experimentation script
  insurance_agent.py           Builds and runs the LangGraph StateGraph, extracts the persisted claim's ObjectId
  agent_definition.py           System prompt + create_agent(); binds tools to the chat LLM
  agent_llm.py                  get_llm(): constructs the ChatBedrockConverse client
  agent_node_definition.py      LangGraph node wiring (chatbot_node, tool_node)
  agent_tools.py                fetch_guidelines, persist_data, clean_chat_history tools; vector store wiring
  agent_vector_store.py         create_vector_store(): MongoDBAtlasVectorSearch factory
  embeddings/bedrock/           Bedrock client + embedding getters (getters.py, client.py, cohere_embeddings.py)
  scripts/
    create_vector_search_index.py   Idempotent creation of the description_index vector index
    seed_policy_documents.py         Idempotent seeding of sample policy_documents
  test_photos/                 Sample accident photos for manual testing
frontend/
  app/api/image-descriptor/route.js   Next.js route proxying to backend POST /imageDescriptor
  app/api/run-agent/route.js          Next.js route proxying to backend POST /runAgent
```

Notable files:

- `backend/agent_tools.py` — defines `INDEX_NAME = "description_index"` and the vector
  store's `embedding_key`/`text_key`; must stay in sync with
  `backend/scripts/create_vector_search_index.py`'s index definition. See
  [EDD.md](./EDD.md) for the exact fields.
- `backend/agent_definition.py` — the system prompt is the only place that specifies
  the shape of a `processed_claims` document (`date`, `description`, `recommendation`,
  `claim_handler`); there is no schema enforcing it.
- `backend/main.py` — holds `image_description` as a module-level global between the
  `/imageDescriptor` and `/runAgent` calls; the two requests are not otherwise linked
  (no session/claim ID), so concurrent uploads from different users will race.

## Environment variables and configuration

Backend (`backend/.env`, loaded via `python-dotenv`):

| Name | Required | Example | Description |
| --- | --- | --- | --- |
| `MONGODB_URI` | yes | `mongodb+srv://...` | Atlas connection string. Must be Atlas, not a local `mongod` — index creation in `scripts/create_vector_search_index.py` calls `create_search_index`, which only exists on Atlas. |
| `DATABASE_NAME` | yes | `insurance_claims` | Database holding all three collections. |
| `COLLECTION_NAME` | yes | `policy_documents` | Guideline documents searched by `fetch_guidelines`. |
| `COLLECTION_NAME_2` | yes | `processed_claims` | Claim summaries written by `persist_data` and read back by `POST /runAgent`. |
| `CHAT_HISTORY_COLLECTION` | yes | `chat_history` | Cleared by `clean_chat_history` at the end of each agent run (see [EDD.md](./EDD.md) known inconsistency: nothing currently writes to it). |
| `AWS_ACCESS_KEY_ID` | yes* | — | Bedrock + (if used) AWS SDK credentials. |
| `AWS_SECRET_ACCESS_KEY` | yes* | — | Paired with the above. |
| `AWS_REGION` | yes | `us-east-1` | Region for Bedrock (`bedrock-runtime`) calls; read in `agent_llm.py`, `pic2textApi.py`, `embeddings/bedrock/getters.py`, `embeddings/bedrock/client.py`. |
| `AWS_DEFAULT_REGION` | no | `us-east-1` | Fallback read by `embeddings/bedrock/client.py` if `AWS_REGION` is unset. |
| `AWS_PROFILE` | no | — | Alternative to explicit keys; read by `embeddings/bedrock/client.py` for local SSO/profile-based credentials. |

\* Not required if running with an `AWS_PROFILE` or the Docker Compose setup, which
mounts `~/.aws/credentials` into the backend container instead.

Frontend (`frontend/.env.local`):

| Name | Required | Example | Description |
| --- | --- | --- | --- |
| `NEXT_PUBLIC_API_BASE` | yes for local dev | `http://localhost:8080` | Backend base URL used by the Next.js API routes (`app/api/image-descriptor/route.js`, `app/api/run-agent/route.js`) when `INTERNAL_API_URL` is unset. |
| `INTERNAL_API_URL` | no | `http://insurance-agentic-backend:8080` | Takes priority over `NEXT_PUBLIC_API_BASE`; used in Docker Compose / Kubernetes so the browser-facing URL isn't required for server-to-server calls. Set automatically by `docker-compose.yml` for the Docker flow. |

Constraints worth knowing before you debug a failure:

- **Atlas is required, not optional.** `scripts/create_vector_search_index.py` calls
  `collection.create_search_index(...)`, which only exists on Atlas clusters (or Atlas
  Search-enabled local deployments) — against a plain community `mongod`, the script
  will connect fine and then fail on index creation.
- **The vector index must be created and the guidelines seeded before `fetch_guidelines`
  returns anything useful.** An unseeded `policy_documents` collection makes
  `vector_store.similarity_search_with_score()` return `[]`, and `fetch_guidelines`
  indexes into that empty result (`result[0][0]`), raising an `IndexError` inside the
  agent run.
- **Embedding dimensions are hardcoded in two places that must agree**:
  `scripts/create_vector_search_index.py`'s `DIMENSIONS = 1024` and the output size of
  `cohere.embed-english-v3` used everywhere embeddings are generated. Changing the
  embedding model without updating the index (and re-seeding) breaks retrieval.
- **`/imageDescriptor` and `/runAgent` share state through a global variable**
  (`image_description` in `backend/main.py`), not a request parameter or database
  record — there is no isolation between concurrent users of the deployed app.

## MongoDB Skills

Use the official MongoDB agent skills from https://github.com/mongodb/agent-skills
whenever the task is MongoDB-specific and a matching skill exists.

## When To Use EDD.md

Use [EDD.md](./EDD.md) as the source of truth for the MongoDB data model in this repository.

Consult [EDD.md](./EDD.md) before making changes that touch:

- MongoDB collections, document structure, or field names
- FastAPI routes that read or write database records
- Validation, form fields, API payloads, or UI that depend on persisted data
- Schema documentation, Mermaid diagrams, or entity modeling discussions
