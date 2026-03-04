from app.github import should_skip, prioritize_files, build_tree

def test_should_skip_binary_extensions():
    assert should_skip("image.png") is True
    assert should_skip("photo.jpg") is True
    assert should_skip("icon.ico") is True
    assert should_skip("font.woff") is True

def test_should_skip_lock_files():
    assert should_skip("yarn.lock") is True
    assert should_skip("package-lock.json") is False  # package-lock.json doesn't match .lock suffix. Wait, .lock is in SKIP_EXTENSIONS.
    # Actually wait let's check what app.github does: `.suffix.lower() in SKIP_EXTENSIONS` so only if it ends with .lock
    assert should_skip("Cargo.lock") is True

def test_should_skip_node_modules():
    assert should_skip("node_modules/express/index.js") is True

def test_should_skip_dist_dir():
    assert should_skip("dist/bundle.js") is True

def test_should_not_skip_python_files():
    assert should_skip("main.py") is False

def test_should_not_skip_readme():
    assert should_skip("README.md") is False

def test_prioritize_files_readme_first():
    blobs = [
        {"type": "blob", "path": "main.py"},
        {"type": "blob", "path": "README.md"}
    ]
    result = prioritize_files(blobs)
    assert result[0] == "README.md"
    assert "main.py" in result

def test_prioritize_files_skips_binaries():
    blobs = [
        {"type": "blob", "path": "logo.png"},
        {"type": "blob", "path": "main.py"}
    ]
    result = prioritize_files(blobs)
    assert "logo.png" not in result
    assert "main.py" in result

def test_prioritize_files_limits_source_files():
    blobs = [{"type": "blob", "path": f"file{i}.py"} for i in range(10)]
    result = prioritize_files(blobs)
    # Priority 3 (source files) should be limited to 5
    assert len(result) == 5

def test_build_tree_top_level_only():
    blobs = [
        {"type": "blob", "path": "file.txt"},
        {"type": "blob", "path": "dir/file.txt"},
        {"type": "blob", "path": "dir/subdir/file.txt"}
    ]
    tree = build_tree(blobs)
    assert "file.txt" in tree
    assert "dir/" in tree
    assert "subdir" not in tree

def test_build_tree_respects_max_chars():
    blobs = [{"type": "blob", "path": f"dir_{i}/file.txt"} for i in range(500)]
    tree = build_tree(blobs, max_chars=2000)
    assert len(tree) == 2000
