import pytest
from app.context import build_context, FILE_BUDGET, MAX_FILE_CHARS

def test_build_context_respects_budget():
    tree = "tree"
    # To exceed FILE_BUDGET (15000), since each file is capped at ~3000 chars,
    # we need at least 6 files to exceed the budget.
    files = {
        f"file{i}.txt": "x" * 3000 for i in range(6)
    }
    context = build_context(tree, files)
    # Budget check allows overhead of file headers, but should not include file5.txt entirely
    assert "file5.txt" not in context

def test_build_context_truncates_large_files():
    tree = "tree"
    files = {
        "large.txt": "b" * (MAX_FILE_CHARS + 100)
    }
    context = build_context(tree, files)
    assert "... [truncated]" in context
    # Verify exact length of 'b's to avoid counting 'a's in filenames or truncation messages
    assert context.count("b") == MAX_FILE_CHARS

def test_build_context_includes_tree():
    tree = "my_special_tree_string"
    files = {"file.txt": "content"}
    context = build_context(tree, files)
    assert context.startswith(tree)

def test_build_context_empty_files():
    tree = "tree_only"
    files = {}
    context = build_context(tree, files)
    assert context == "tree_only\n\n"

def test_build_context_file_order_preserved():
    tree = "tree"
    files = {
        "z.txt": "content z",
        "a.txt": "content a",
        "m.txt": "content m"
    }
    context = build_context(tree, files)

    idx_z = context.find("=== z.txt ===")
    idx_a = context.find("=== a.txt ===")
    idx_m = context.find("=== m.txt ===")

    assert idx_z < idx_a < idx_m
