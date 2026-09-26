"""CLI: python -m deepagent "your research question" or deepagent "question" """

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure package and root are on sys.path
_AGENT_ROOT = Path(__file__).resolve().parents[2]
if str(_AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(_AGENT_ROOT))
if str(_AGENT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_AGENT_ROOT / "src"))

from deepagent.agent import build_agent, extract_final_answer, run_research, stream_research
from deepagent.config import get_settings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="deepagent",
        description="DeepAgent: Single-command DeepSeek research agent with streaming output.",
    )
    parser.add_argument("question", nargs="+", help="Research question, URL, file, or topic to investigate")
    parser.add_argument(
        "--model", default=None, help="Override DEEPSEEK_MODEL (e.g. deepseek-chat or deepseek-reasoner)"
    )
    parser.add_argument(
        "--no-stream", action="store_true", help="Disable real-time streaming output"
    )
    args = parser.parse_args(argv)

    settings = get_settings()
    if args.model:
        settings.deepseek_model = args.model
    try:
        settings.validate()
    except (RuntimeError, ValueError) as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    question = " ".join(args.question)
    print(f"[deepagent] model={settings.deepseek_model} streaming={not args.no_stream}")
    print(f"[deepagent] question: {question!r}\n")

    try:
        if args.no_stream:
            result = run_research(question, settings)
            print("\n=== FINAL REPORT ===\n")
            print(extract_final_answer(result) or result)
        else:
            current_node = None
            for event_type, payload in stream_research(question, settings):
                if event_type == "token":
                    sys.stdout.write(payload)
                    sys.stdout.flush()
                elif event_type == "node" and payload != current_node:
                    current_node = payload
                    if current_node in ("planner", "researcher", "verifier", "synthesizer", "tools"):
                        sys.stdout.write(f"\n[{current_node}] ")
                        sys.stdout.flush()
                elif event_type == "tool_result":
                    tool_name = payload.get("name", "tool")
                    sys.stdout.write(f" [{tool_name} completed] ")
                    sys.stdout.flush()
            print()
    except KeyboardInterrupt:
        print("\n[deepagent] Execution interrupted by user.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"\n[deepagent] Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
