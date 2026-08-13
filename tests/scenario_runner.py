"""
Drives the compiled graph with a scripted job description + a list of
follow-up replies, and returns the raw conversation as clean text (no
terminal/Rich formatting) - used both to regenerate tests/test_scenarios.md
and as a lightweight smoke test you can run in CI.

Usage:
    python tests/scenario_runner.py --jd data/job_descriptions/senior_frontend_react.txt \\
        --mode mock \\
        --say "Compare the top 3 matches side by side" \\
        --say "Why did John rank higher than Jane?" \\
        --say "That's all, thanks"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.types import Command

from src import config
from src.state import new_state


def run_scenario(jd_text: str, replies: list[str], mode: str = "mock", thread_id: str = "scenario") -> list[dict]:
    """Returns a list of {"role": "you"|"agent", "content": str} turns, in order."""
    config.set_mode(mode)
    # local import so config.MODE is resolved before matching_agent builds the graph
    from matching_agent import build_graph

    graph = build_graph()
    thread_config = {"configurable": {"thread_id": thread_id}}

    transcript: list[dict] = []

    def _record_new(messages: list, seen: int) -> int:
        for msg in messages[seen:]:
            if isinstance(msg, HumanMessage) and msg.content:
                transcript.append({"role": "you", "content": msg.content})
            elif isinstance(msg, AIMessage) and msg.content:
                transcript.append({"role": "agent", "content": msg.content})
        return len(messages)

    result = graph.invoke(new_state(job_description_raw=jd_text), config=thread_config)
    seen = _record_new(result["messages"], 0)

    for reply in replies:
        if "__interrupt__" not in result:
            break
        result = graph.invoke(Command(resume=reply), config=thread_config)
        seen = _record_new(result["messages"], seen)

    return transcript


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--jd", required=True)
    parser.add_argument("--mode", default="mock", choices=["mock", "live", "auto"])
    parser.add_argument("--say", action="append", default=[], dest="replies")
    args = parser.parse_args()

    jd_text = Path(args.jd).read_text(encoding="utf-8")
    transcript = run_scenario(jd_text, args.replies, mode=args.mode)
    for turn in transcript:
        label = "**You:**" if turn["role"] == "you" else "**Agent:**"
        print(f"{label} {turn['content']}\n")


if __name__ == "__main__":
    main()
