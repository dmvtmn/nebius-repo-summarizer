# Repo Summarizer

A FastAPI service that takes a GitHub repository URL and returns a human-readable summary of the project: what it does, what technologies are used, and how it's structured.

## Prerequisites

- Python 3.10+

## Setup

1. Clone the repository:
   git clone https://github.com/dmvtmn/nebius-repo-summarizer.git
   cd nebius-repo-summarizer

2. Create and activate a virtual environment:
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

3. Install dependencies:
   pip install -r requirements.txt

4. Configure environment variables:
   cp .env.example .env
   # Edit .env and set your NEBIUS_API_KEY
   # Optionally set GITHUB_TOKEN to avoid GitHub rate limits

## Run

   uvicorn app.main:app --reload

The server starts at http://localhost:8000

## Test

   curl -X POST http://localhost:8000/summarize \
     -H "Content-Type: application/json" \
     -d '{"github_url": "https://github.com/nebius/token-factory-cookbook"}'

You can also use the interactive docs at http://localhost:8000/docs

## Model Choice

I went with meta-llama/Llama-3.3-70B-Instruct-fast via Nebius Token Factory. It handles structured JSON output reliably and the -fast variant keeps latency reasonable for a synchronous API call. Good balance between quality and cost for this use case.


## Context Strategy

Not all files are worth sending to the LLM. The approach here is to prioritize the README and manifest files (pyproject.toml, package.json, etc.) since they give the most signal about what a project does. Root-level source files and CI workflows come next. Binaries, lock files, and noise directories like node_modules are skipped entirely. Each file is capped at 3,000 chars and the total context stays under 15,000 — the directory tree is always included at the top so the model gets structural context even when files are trimmed.


## Configuration

| Variable | Required | Description |
|---|---|---|
| NEBIUS_API_KEY | Yes | Nebius Token Factory API key |
| GITHUB_TOKEN | No | GitHub personal access token — raises rate limit from 60 to 5,000 req/hour |
