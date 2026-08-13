#!/usr/bin/env python3
"""
matching_agent.py — Resume Matching Agent (LangGraph)

This is the required Part-A deliverable: the LangGraph agent that screens
resumes against a job description in three rounds, then hands control to a
human-feedback loop where you can compare candidates, ask why one ranked
higher than another, request interview questions, get a hire/no-hire call,
or adjust the requirements and have it re-rank.

Graph shape (exactly as specified in the assignment brief):

    START -> parse_jd -> extract_requirements -> search_resumes ->
    rank_candidates -> generate_report -> human_feedback -> END

human_feedback is a real interrupt() pause (see src/graph/nodes.py) with two
loop-back edges: refining the requirements routes back into rank_candidates
(a genuine re-rank against the already-retrieved pool), and anything else
either answers in place and stays in the loop, or ends the session.

Usage:
    python matching_agent.py                  # auto-detect mode (live if
                                                # GROQ_API_KEY is set, else mock)
    python matching_agent.py --mode mock       # force the offline rule-based mode
    python matching_agent.py --mode live       # force Groq + local embeddings
    python matching_agent.py --jd data/job_descriptions/senior_frontend_react.txt
"""

from __future__ import annotations

import argparse
import sys

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from src import config, tools
from src.graph.nodes import (
    extract_requirements_node,
    generate_report_node,
    human_feedback_node,
    parse_jd,
    rank_candidates_node,
    route_after_feedback,
    search_resumes_node,
)
from src.state import AgentState, new_state

console = Console()


# --------------------------------------------------------------------------
# Graph construction — this is Part A.1's "Agent Workflow (Graph Structure)"
# --------------------------------------------------------------------------

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("parse_jd", parse_jd)
    graph.add_node("extract_requirements", extract_requirements_node)
    graph.add_node("search_resumes", search_resumes_node)
    graph.add_node("rank_candidates", rank_candidates_node)
    graph.add_node("generate_report", generate_report_node)
    graph.add_node("human_feedback", human_feedback_node)

    graph.add_edge(START, "parse_jd")
    graph.add_edge("parse_jd", "extract_requirements")
    graph.add_edge("extract_requirements", "search_resumes")
    graph.add_edge("search_resumes", "rank_candidates")
    graph.add_edge("rank_candidates", "generate_report")
    graph.add_edge("generate_report", "human_feedback")

    # Requirement refinements loop back into rank_candidates directly (the
    # full pool was already retrieved by search_resumes, so re-ranking
    # against it is enough - no need to re-query). Anything else either
    # stays in the feedback loop or ends the session.
    graph.add_conditional_edges(
        "human_feedback",
        route_after_feedback,
        {"rerank": "rank_candidates", "continue": "human_feedback", "end": END},
    )

    return graph.compile(checkpointer=MemorySaver())


# --------------------------------------------------------------------------
# CLI driver
# --------------------------------------------------------------------------

def _pick_job_description() -> str:
    samples = tools.list_job_descriptions.invoke({})
    console.print("\n[bold]How would you like to provide the job description?[/bold]")
    for i, name in enumerate(samples, 1):
        console.print(f"  {i}. {name}")
    console.print(f"  {len(samples) + 1}. Paste my own (end with a blank line)")

    choice = console.input("\n> ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(samples):
        return tools.read_job_description.invoke({"filename": samples[int(choice) - 1]})

    console.print("[dim]Paste the job description, then press Enter on an empty line to finish:[/dim]")
    lines = []
    while True:
        line = input()
        if not line.strip():
            break
        lines.append(line)
    return "\n".join(lines)


def _print_ai_messages(messages: list, already_printed: int) -> int:
    from langchain_core.messages import AIMessage
    for msg in messages[already_printed:]:
        if isinstance(msg, AIMessage) and msg.content:
            console.print(Panel(Markdown(msg.content), border_style="cyan", title="Agent", title_align="left"))
    return len(messages)


def run_cli(jd_path: str | None = None) -> None:
    mode = config.MODE
    banner = (
        f"[bold]Resume Matching Agent[/bold]  ·  mode: [{'green' if mode == 'live' else 'yellow'}]{mode}[/]"
    )
    if mode == "mock":
        banner += "\n[dim]No GROQ_API_KEY found (or --mode mock forced) — running fully offline, " \
                   "rule-based reasoning. Set GROQ_API_KEY in .env for live LLM reasoning.[/dim]"
    console.print(Panel(banner, border_style="blue"))

    if jd_path:
        with open(jd_path, encoding="utf-8") as f:
            jd_text = f.read()
    else:
        jd_text = _pick_job_description()

    if not jd_text.strip():
        console.print("[red]No job description provided — exiting.[/red]")
        return

    graph = build_graph()
    thread_config = {"configurable": {"thread_id": "cli-session"}}

    result = graph.invoke(new_state(job_description_raw=jd_text), config=thread_config)
    printed = _print_ai_messages(result["messages"], 0)

    while "__interrupt__" in result:
        try:
            user_reply = console.input("\n[bold green]You:[/bold green] ")
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Ending session.[/dim]")
            break
        result = graph.invoke(Command(resume=user_reply), config=thread_config)
        printed = _print_ai_messages(result["messages"], printed)

    console.print("\n[dim]Session ended.[/dim]")


def main():
    parser = argparse.ArgumentParser(description="Resume Matching Agent (LangGraph)")
    parser.add_argument("--mode", choices=["auto", "live", "mock"], default="auto",
                         help="auto (default): live if GROQ_API_KEY is set, else mock")
    parser.add_argument("--jd", dest="jd_path", default=None,
                         help="Path to a job description file (skips the interactive picker)")
    args = parser.parse_args()

    config.set_mode(args.mode)
    try:
        run_cli(jd_path=args.jd_path)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
