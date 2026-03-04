FILE_BUDGET = 15000
MAX_FILE_CHARS = 3000

def build_context(tree: str, files: dict[str, str]) -> str:
    parts = [tree, "\n\n"]
    remaining = FILE_BUDGET
    for path, content in files.items():
        if remaining <= 0:
            break
        truncated = content[:MAX_FILE_CHARS]
        if len(content) > MAX_FILE_CHARS:
            truncated += "\n... [truncated]"
        section = f"=== {path} ===\n{truncated}\n\n"
        parts.append(section)
        remaining -= len(truncated)
    return "".join(parts)
