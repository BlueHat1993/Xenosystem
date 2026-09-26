"""Single-command runner for DeepAgent from workspace root.

Usage:
    python run.py "your research question"
    python run.py "https://github.com/langchain-ai/deepagents" --model deepseek-reasoner
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure deepagent and deepagent/src are discoverable
ROOT = Path(__file__).resolve().parent / "deepagent"
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from deepagent.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
