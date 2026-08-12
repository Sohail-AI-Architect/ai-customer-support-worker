"""Vercel function entrypoint for the FastAPI backend.

Vercel loads the function with the repository root on ``sys.path``, so the
app's ``src`` package must be added explicitly before importing it. Keep this
file at ``backend/serve.py`` (see ``vercel.json`` build config).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from main import app as _app  # noqa: E402

app = _app
