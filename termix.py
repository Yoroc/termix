#!/usr/bin/env python3
"""
Termix: Capture shell history, git status/diff, and project structure for LLM context.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Optional

import typer

app = typer.Typer(help="Termix: Capture shell history, git status/diff, and project structure for LLM context.")


def get_shell_history(shell: str, count: int) -> List[str]:
    """Retrieve last N commands from shell history file."""
    home = Path.home()
    if shell == "bash":
        history_file = home / ".bash_history"
    elif shell == "zsh":
        history_file = home / ".zsh_history"
    else:
        return []

    if not history_file.exists():
        return []

    try:
        content = history_file.read_text(encoding="utf-8", errors="ignore")
        lines = content.splitlines()
        cleaned = []
        for line in reversed(lines):
            if not line.strip():
                continue
            if shell == "zsh" and line.startswith(":"):
                parts = line.split(";")
                if len(parts) > 1:
                    cmd = parts[-1].strip()
                    if cmd:
                        cleaned.append(cmd)
                else:
                    cleaned.append(line.strip())
            else:
                cleaned.append(line.strip())
            if len(cleaned) >= count:
                break
        return list(reversed(cleaned))
    except Exception:
        return []


def get_git_status() -> Optional[str]:
    """Get git status in porcelain format."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def get_git_diff() -> Optional[str]:
    """Get git diff (staged and unstaged)."""
    try:
        result = subprocess.run(
            ["git", "diff"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def get_project_structure(
    root: Path, max_depth: int = 3, ignore_dirs: Optional[List[str]] = None
) -> str:
    """Generate a tree-like structure of the project."""
    if ignore_dirs is None:
        ignore_dirs = {
            ".git",
            "node_modules",
            "__pycache__",
            ".venv",
            "venv",
            "env",
            ".idea",
            ".vscode",
            "dist",
            "build",
            ".parcel-cache",
            ".cache",
        }

    lines = []

    def _walk(dir_path: Path, prefix: str = "", depth: int = 0):
        if depth > max_depth:
            return
        try:
            entries = sorted(dir_path.iterdir(), key=lambda e: (e.is_file(), e.name.lower()))
        except PermissionError:
            return

        filtered = []
        for entry in entries:
            if entry.is_dir() and entry.name in ignore_dirs:
                continue
            if entry.is_file():
                ext = entry.suffix.lower()
                if ext in {
                    ".pyc",
                    ".exe",
                    ".so",
                    ".dll",
                    ".obj",
                    ".o",
                    ".a",
                    ".lib",
                    ".zip",
                    ".tar",
                    ".gz",
                    ".rar",
                    ".7z",
                    ".png",
                    ".jpg",
                    ".jpeg",
                    ".gif",
                    ".bmp",
                    ".ico",
                    ".pdf",
                    ".zip",
                    ".tar",
                    ".gz",
                }:
                    continue
            filtered.append(entry)

        for i, entry in enumerate(filtered):
            is_last = i == len(filtered) - 1
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{entry.name}")
            if entry.is_dir() and depth < max_depth:
                extension = "    " if is_last else "│   "
                _walk(entry, prefix + extension, depth + 1)

    _walk(root)
    return "\n".join(lines)


@app.command()
def main(
    num_history: int = typer.Option(10, "--num-history", "-n", help="Number of history commands to capture."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path. If not provided, prints to stdout."),
    no_git: bool = typer.Option(False, "--no-git", help="Skip git status and diff."),
    no_structure: bool = typer.Option(False, "--no-structure", help="Skip project structure."),
    depth: int = typer.Option(3, "--depth", help="Maximum depth for project structure traversal."),
):
    """Generate Markdown context for LLMs."""
    # Determine shell
    shell = os.environ.get("SHELL", "").split("/")[-1]
    if shell not in ("bash", "zsh"):
        # Try to detect from process
        shell = "bash" if os.name != "nt" else "bash"  # default to bash on Unix, assume bash on Windows if WSL/Git Bash
        # On Windows, we might still have bash/zsh via WSL or Git Bash
        # We'll try both
        shells_to_try = ["bash", "zsh"]
    else:
        shells_to_try = [shell]

    history_lines = []
    for sh in shells_to_try:
        history_lines = get_shell_history(sh, num_history)
        if history_lines:
            break

    git_status = None if no_git else get_git_status()
    git_diff = None if no_git else get_git_diff()
    structure = None if no_structure else get_project_structure(Path.cwd(), max_depth=depth)

    # Build Markdown
    md_parts = []

    md_parts.append("# Termix Context\n")

    if history_lines:
        md_parts.append("## Shell History (last {} commands)".format(len(history_lines)))
        md_parts.append("```bash")
        md_parts.extend(history_lines)
        md_parts.append("```\n")

    if git_status is not None:
        md_parts.append("## Git Status")
        md_parts.append("```")
        md_parts.append(git_status if git_status else "Working tree clean")
        md_parts.append("```\n")

    if git_diff is not None:
        md_parts.append("## Git Diff")
        md_parts.append("```diff")
        md_parts.append(git_diff if git_diff else "No changes")
        md_parts.append("```\n")

    if structure is not None:
        md_parts.append("## Project Structure")
        md_parts.append("```text")
        md_parts.append(structure if structure else "(empty)")
        md_parts.append("```\n")

    markdown = "\n".join(md_parts)

    if output:
        output.write_text(markdown, encoding="utf-8")
        typer.secho(f"Context written to {output}", fg=typer.colors.GREEN)
    else:
        typer.echo(markdown)


if __name__ == "__main__":
    app()