import os
import json
from openai import AsyncOpenAI
from pydantic import BaseModel

class RepoSummary(BaseModel):
    summary: str
    technologies: list[str]
    structure: str

SYSTEM_PROMPT = "You are an experienced software engineer. Given a set of repository files, return a JSON object summarising what the project does, what technologies it uses, and how it's structured."

USER_PROMPT_TEMPLATE = """Analyze this GitHub repository and provide:
1. summary: 2-4 sentence description of what the project does and its purpose
2. technologies: list of main languages, frameworks, libraries, and tools used
3. structure: 1-2 sentences describing how the codebase is organized

Repository contents:
{context}"""

async def summarize_with_llm(context: str) -> RepoSummary:
    client = AsyncOpenAI(
        base_url="https://api.studio.nebius.com/v1/",
        api_key=os.getenv("NEBIUS_API_KEY")
    )
    response = await client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct-fast",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT_TEMPLATE.format(context=context)}
        ],
        response_format={"type": "json_object"},
        temperature=0.2
    )
    raw = response.choices[0].message.content
    return RepoSummary(**json.loads(raw))
