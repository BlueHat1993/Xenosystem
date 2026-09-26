"""Runnable example for DeepAgent research.

Usage:
    python examples/run_research.py "your research question"
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root and src to path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from deepagent.cli import main

if __name__ == "__main__":
    query_args = sys.argv[1:] if len(sys.argv) > 1 else ["What is DeepSeek-V3 and how does it work?"]
    raise SystemExit(main(query_args))
