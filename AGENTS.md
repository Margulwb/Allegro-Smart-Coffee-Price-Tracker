# Agent Instructions

## Terminal Commands

- This repository runs in WSL (AlmaLinux), under `/home/mg/git/Allegro-Smart-Coffee-Price-Tracker`. Use the WSL/POSIX shell and repository root; do not assume PowerShell paths or commands.
- When a task calls for tests, linting, installing dependencies, or launching the app, execute the relevant command with the available terminal tool and report the command and result. Do not only tell the user to run it.
- Commands run through the agent's terminal are separate from the user's visible VS Code terminal. Report their output in chat; never claim the user can see those commands running live. If the user needs to run a command in their own terminal, provide the exact command and say that they need to run it there.
- Prefer the repository virtual environment when present: `.venv/bin/python -m pytest`, `.venv/bin/python -m ruff check .`, and `.venv/bin/python -m uvicorn app.main:app --reload`. The server command is for requests to launch the app; keep it running in the background and report its URL.
- If development dependencies are missing, install the declared set from the repository root with `.venv/bin/python -m pip install -e '.[dev]'`. Create `.venv` with `python3 -m venv .venv` only when it does not exist.
- Avoid destructive or system-wide commands. Inspect the target and explain the impact before running a command that deletes data, rewrites history, or changes the host environment; ask for approval when the impact is not clearly authorized.

## Project Checks

- Python 3.11 or newer is required.
- Run tests with `.venv/bin/python -m pytest` and lint with `.venv/bin/python -m ruff check .` from the repository root.
- The FastAPI application entry point is `app.main:app`; run it with `.venv/bin/python -m uvicorn app.main:app --reload` when asked to launch it.