import asyncio
import base64
import os
from pathlib import PurePosixPath
import httpx

SKIP_EXTENSIONS = {".lock", ".min.js", ".min.css", ".png", ".jpg", ".jpeg",
                   ".gif", ".svg", ".ico", ".woff", ".ttf", ".zip", ".tar.gz", ".pyc"}
SKIP_DIRS = {"node_modules", "dist", "build", ".git", "__pycache__", ".venv", "vendor"}

PRIORITY_1 = {"readme.md", "readme.rst", "readme.txt"}
PRIORITY_2 = {"pyproject.toml", "setup.py", "setup.cfg", "package.json",
               "cargo.toml", "go.mod", "pom.xml", "build.gradle"}

def get_github_headers() -> dict:
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

def should_skip(path: str) -> bool:
    p = PurePosixPath(path)
    if any(part in SKIP_DIRS for part in p.parts):
        return True
    if p.suffix.lower() in SKIP_EXTENSIONS:
        return True
    return False

def prioritize_files(blobs: list[dict]) -> list[str]:
    p1, p2, p3, p4 = [], [], [], []
    for item in blobs:
        if item["type"] != "blob":
            continue
        path = item["path"]
        if should_skip(path):
            continue
        name = PurePosixPath(path).name.lower()
        depth = path.count("/")
        if name in PRIORITY_1:
            p1.append(path)
        elif name in PRIORITY_2:
            p2.append(path)
        elif path.startswith(".github/workflows/") and path.endswith(".yml"):
            p4.append(path)
        elif depth <= 1 and PurePosixPath(path).suffix in {".py", ".ts", ".go", ".rs", ".js"}:
            p3.append(path)
    return p1 + p2 + p3[:5] + p4[:2]

def build_tree(blobs: list[dict], max_chars: int = 2000) -> str:
    dirs = set()
    for item in blobs:
        if item["type"] != "blob":
            continue
        parts = item["path"].split("/")
        if len(parts) >= 2:
            dirs.add(parts[0] + "/")
        if len(parts) == 1:
            dirs.add(parts[0])
    tree = "Repository structure:\n" + "\n".join(sorted(dirs))
    return tree[:max_chars]

async def fetch_file_content(client: httpx.AsyncClient, owner: str, repo: str, path: str) -> tuple[str, str]:
    try:
        r = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}/contents/{path}",
            headers=get_github_headers(),
            timeout=10.0
        )
        r.raise_for_status()
        data = r.json()
        content = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        return path, content
    except Exception as e:
        return path, f"[Error fetching file: {e}]"

async def fetch_repo_data(owner: str, repo: str) -> dict:
    async with httpx.AsyncClient() as client:
        tree_resp = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}/git/trees/HEAD?recursive=1",
            headers=get_github_headers(),
            timeout=15.0
        )
        if tree_resp.status_code == 404:
            raise ValueError("not_found")
        if tree_resp.status_code == 403:
            raise ValueError("rate_limited")
        tree_resp.raise_for_status()

        blobs = tree_resp.json().get("tree", [])
        selected_paths = prioritize_files(blobs)
        tree_str = build_tree(blobs)

        tasks = [fetch_file_content(client, owner, repo, p) for p in selected_paths]
        results = await asyncio.gather(*tasks, return_exceptions=False)

        return {"tree": tree_str, "files": dict(results)}
