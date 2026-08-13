"""
app_streamlit.py — Streamlit chat interface for the Resume Matching Agent.

Thin UI layer over the same compiled graph matching_agent.py uses - no
agent logic lives here. Run with:

    streamlit run app_streamlit.py
"""

from __future__ import annotations

import uuid
from pathlib import Path

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.types import Command

from src import config, tools

st.set_page_config(page_title="Resume Matching Agent", page_icon="🎯", layout="wide")


# --------------------------------------------------------------------------
# Session bootstrap
# --------------------------------------------------------------------------

def _init_session(mode: str) -> None:
    config.set_mode(mode)
    from matching_agent import build_graph  # imported after mode is set

    st.session_state.graph = build_graph()
    st.session_state.thread_config = {"configurable": {"thread_id": f"st-{uuid.uuid4().hex[:8]}"}}
    st.session_state.started = False
    st.session_state.done = False
    st.session_state.display_messages = []  # [{"role": "user"/"assistant", "content": str}]
    st.session_state.seen_count = 0
    st.session_state.last_result = None
    st.session_state.resolved_mode = config.MODE


def _sync_new_messages(result: dict) -> None:
    from langchain_core.messages import BaseMessage

    messages: list[BaseMessage] = result.get("messages", [])
    for msg in messages[st.session_state.seen_count:]:
        if isinstance(msg, HumanMessage) and msg.content:
            st.session_state.display_messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage) and msg.content:
            st.session_state.display_messages.append({"role": "assistant", "content": msg.content})
    st.session_state.seen_count = len(messages)
    st.session_state.last_result = result
    st.session_state.done = "__interrupt__" not in result


# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------

with st.sidebar:
    st.title("🎯 Resume Matching Agent")
    st.caption("LangGraph agent · multi-round resume screening")

    mode_choice = st.radio(
        "Mode", ["auto", "mock", "live"], index=0,
        help="auto: live if GROQ_API_KEY is set, else mock. "
             "mock: fully offline, rule-based - no API key needed. "
             "live: Groq LLM + local embeddings.",
    )

    if st.button("🔄 New session", use_container_width=True):
        _init_session(mode_choice)
        st.rerun()

    if "graph" not in st.session_state:
        _init_session(mode_choice)

    resolved = st.session_state.get("resolved_mode", "mock")
    badge = "🟢 live" if resolved == "live" else "🟡 mock (offline)"
    st.markdown(f"**Active mode:** {badge}")
    if resolved == "mock":
        st.caption("Set GROQ_API_KEY in .env and start a new session for live LLM reasoning.")

    st.divider()

    if st.session_state.get("last_result"):
        req = st.session_state.last_result.get("requirements")
        shortlist = st.session_state.last_result.get("shortlist", [])
        if req:
            st.markdown(f"**Role:** {req.get('role_title', 'n/a')}")
            st.markdown(f"**Seniority:** {req.get('seniority', 'n/a')}")
            st.markdown(f"**Min experience:** {req.get('min_years_experience', 0)}+ yrs")
            st.markdown(f"**Round:** {st.session_state.last_result.get('round', 1)}/3")
        if shortlist:
            st.markdown("**Current top 5:**")
            for c in shortlist[:5]:
                st.markdown(f"- {c['name']} — {c['score']:.0f}/100")

        report_path = st.session_state.last_result.get("last_report_path")
        if report_path and Path(report_path).exists():
            st.download_button(
                "⬇️ Download full report",
                data=Path(report_path).read_text(encoding="utf-8"),
                file_name=Path(report_path).name,
                mime="text/markdown",
                use_container_width=True,
            )


# --------------------------------------------------------------------------
# Main area
# --------------------------------------------------------------------------

if not st.session_state.started:
    st.header("Start a screening")
    st.write("Pick a sample job description or paste your own, then start the agent.")

    samples = tools.list_job_descriptions.invoke({})
    choice = st.selectbox("Sample job descriptions", ["(paste my own below)"] + samples)

    if choice != "(paste my own below)":
        default_text = tools.read_job_description.invoke({"filename": choice})
    else:
        default_text = ""

    jd_text = st.text_area("Job description", value=default_text, height=280)

    if st.button("▶ Start screening", type="primary", disabled=not jd_text.strip()):
        from src.state import new_state

        with st.spinner("Screening resumes — parsing, searching, ranking, and analyzing the shortlist..."):
            result = st.session_state.graph.invoke(new_state(job_description_raw=jd_text),
                                                     config=st.session_state.thread_config)
        _sync_new_messages(result)
        st.session_state.started = True
        st.rerun()

else:
    for msg in st.session_state.display_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if st.session_state.done:
        st.info("Session ended. Start a new session from the sidebar to screen another role.")
    else:
        user_input = st.chat_input(
            "Compare candidates, ask why one ranked higher, request interview questions, "
            "get a hire recommendation, or adjust the requirements..."
        )
        if user_input:
            with st.chat_message("user"):
                st.markdown(user_input)
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    result = st.session_state.graph.invoke(
                        Command(resume=user_input), config=st.session_state.thread_config
                    )
            _sync_new_messages(result)
            st.rerun()
