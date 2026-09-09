# termix

![CI](https://github.com/Yoroc/termix/actions/workflows/ci.yml/badge.svg)
![PyPI - Version](https://img.shields.io/pypi/v/termix?style=flat-square)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/termix?style=flat-square)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)

![Demo](./@yoro.svg)

Termix is a CLI tool that captures the last N commands from bash/zsh history, reads the local git status/diff, parses the project folder structure, and combines them into a clean Markdown block ready for LLMs.

## Installation

```bash
pip install typer
```

Or clone the repository and run the script directly.

## Usage

```bash
termix [OPTIONS]
```

Options:
  -n, --num-history INTEGER  Number of history commands to capture. [default: 10]
  -o, --output PATH          Output file path. If not provided, prints to stdout.
  --no-git                   Skip git status and diff.
  --no-structure             Skip project structure.
  --depth INTEGER            Maximum depth for project structure traversal. [default: 3]
  --install-completion       Install completion for the current shell.
  --show-completion          Show completion for the current shell, to copy it or customize.
  --help                     Show this message and exit.

## Example

```bash
termix -n 20 > context.md
```

This will generate a Markdown file with the last 20 commands, git status/diff, and project structure.

## How It Works

- **Shell History**: Reads from `~/.bash_history` or `~/.zsh_history`.
- **Git**: Uses `git status --porcelain` and `git diff`.
- **Project Structure**: Walks the current directory, ignoring common directories like `.git`, `node_modules`, etc.

## Requirements

- Python 3.7+
- Typer

## License

MIT