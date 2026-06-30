# AGENTS.md

## Cursor Cloud specific instructions

This repo is a single static page (`index.html`, vanilla HTML/CSS/JS — no build step) with Python regression tests under `tests/`. See `docs/development.md` for the canonical run/test commands.

### Running the app
- Serve the static file: `python3 -m http.server 8000` from the repo root, then open `http://localhost:8000/`. There is no build/compile step and no app runtime dependencies; edits to `index.html` are picked up on browser refresh.
- Note: this environment has `python3` (not a bare `python`); the docs use `python`.

### Tests / lint
- There is no linter configured in this repo.
- CI (`.github/workflows/tests.yml`) only runs `pytest tests/test_expert_comptable.py` plus the four `test_issue_*.py` files invoked as scripts (`python3 tests/<file>.py`). It does NOT run the whole `tests/` dir through pytest.
- Gotcha: `pytest tests/` reports 4 collection ERRORS in `tests/test_issue*s_23_24_25_26.py`. This is pre-existing and not an environment problem — that file defines helper functions named `test_*` that take positional args, so pytest misreads them as fixtures. Run it as a standalone script instead: `python3 tests/test_issues_23_24_25_26.py` (passes).
