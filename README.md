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
     -d '{"github_url": "https://github.com/psf/requests"}'

You can also use the interactive docs at http://localhost:8000/docs

## Model Choice

meta-llama/Meta-Llama-3.1-70B-Instruct via Nebius Token Factory — strong instruction following with OpenAI-compatible API, cost-efficient for structured JSON extraction tasks.

## Context Strategy

Files are selected by priority: README first, then config/manifest files (pyproject.toml, package.json, etc.), then root-level source files, then CI workflows. Binary files, lock files, and dependency directories (node_modules, dist, .venv) are skipped. Each file is capped at 3,000 characters with a total budget of 15,000 characters, filled greedily in priority order. The directory tree is always prepended to give the LLM structural context.

## Configuration

| Variable | Required | Description |
|---|---|---|
| NEBIUS_API_KEY | Yes | Nebius Token Factory API key |
| GITHUB_TOKEN | No | GitHub personal access token — raises rate limit from 60 to 5,000 req/hour |