"""CLI: python -m deepagent.cli "your research question" """

from __future__ import annotations

import argparse
import sys

sys.path.insert(0, "src")  # allow `python -m deepagent.cli` from repo root

from deepagent.agent import build_agent, extract_final_answer
from deepagent.config import get_settings


def main() -> int:
    parser = argparse.ArgumentParser(description="DeepAgent draft research agent (DeepSeek)")
    parser.add_argument("question", nargs="+", help="Research question to investigate")
    parser.add_argument("--model", default=None, help="Override DEEPSEEK_MODEL, e.g. deepseek-reasoner")
    args = parser.parse_args()

    settings = get_settings()
    if args.model:
        settings.deepseek_model = args.model
    try:
        settings.validate()
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    question = " ".join(args.question)
    print(f"[deepagent] model={settings.deepseek_model} question={question!r}\n")

    agent = build_agent(settings)
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    print(extract_final_answer(result) or result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
