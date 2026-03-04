from dotenv import load_dotenv
load_dotenv()

import re
import sys
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.github import fetch_repo_data
from app.context import build_context
from app.llm import summarize_with_llm
from app import cache

app = FastAPI(title="Repo Summarizer")

GITHUB_URL_RE = re.compile(r"https://github\.com/([^/]+)/([^/]+?)(?:\.git)?$")

class SummarizeRequest(BaseModel):
    github_url: str

@app.post("/summarize")
async def summarize(req: SummarizeRequest):
    match = GITHUB_URL_RE.match(req.github_url.strip())
    if not match:
        return JSONResponse(status_code=422, content={"status": "error", "message": "Invalid GitHub URL format"})

    owner, repo = match.group(1), match.group(2)

    cached = cache.get(req.github_url)
    if cached:
        return JSONResponse(content=cached, headers={"X-Cache": "HIT"})

    try:
        repo_data = await fetch_repo_data(owner, repo)
    except ValueError as e:
        if str(e) == "not_found":
            return JSONResponse(status_code=404, content={"status": "error", "message": "Repository not found or is private"})
        if str(e) == "rate_limited":
            return JSONResponse(status_code=429, content={"status": "error", "message": "GitHub API rate limit exceeded. Set GITHUB_TOKEN to increase limits."})
        return JSONResponse(status_code=400, content={"status": "error", "message": str(e)})
    except Exception as e:
        print(f"GitHub fetch error: {e}", file=sys.stderr)
        return JSONResponse(status_code=502, content={"status": "error", "message": f"Failed to fetch repository: {e}"})

    context = build_context(repo_data["tree"], repo_data["files"])

    try:
        summary = await summarize_with_llm(context)
    except Exception as e:
        print(f"LLM error: {e}", file=sys.stderr)
        return JSONResponse(status_code=502, content={"status": "error", "message": f"LLM service error: {e}"})

    result = summary.model_dump()
    cache.set(req.github_url, result)
    return JSONResponse(content=result, headers={"X-Cache": "MISS"})
