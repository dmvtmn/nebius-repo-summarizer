import os
from openai import AsyncOpenAI
from pydantic import BaseModel

class RepoSummary(BaseModel):
    summary: str
    technologies: list[str]
    structure: str

SYSTEM_PROMPT = "You are a senior software engineer. Analyze the provided repository files and return a structured JSON summary."

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
    response = await client.beta.chat.completions.parse(
        model="meta-llama/Meta-Llama-3.1-70B-Instruct",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT_TEMPLATE.format(context=context)}
        ],
        response_format=RepoSummary,
        temperature=0.2
    )
    return response.choices[0].message.parsed
