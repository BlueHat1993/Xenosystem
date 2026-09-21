"""Minimal example: run a DeepSeek research query.

Usage:
    python examples/run_research.py "your research question"
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from deepagent.agent import build_agent, extract_final_answer
from deepagent.config import get_settings


def main() -> None:
    question = " ".join(sys.argv[1:]) or "What is DeepSeek-V3 and how does it work?"
    settings = get_settings()
    settings.validate()

    print(f"[model] {settings.deepseek_model}")
    agent = build_agent(settings)
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})

    print("\n=== FINAL REPORT ===\n")
    print(extract_final_answer(result) or result)


if __name__ == "__main__":
    main()
