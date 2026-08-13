# State machine diagrams

Two versions of the same graph:

- **`state_machine.mmd`** — hand-labeled for readability, with each node
  annotated with which screening round it belongs to. This is the one
  embedded in the main README.
- **`state_machine.raw.mmd`** — generated directly from the compiled graph
  via `graph.get_graph().draw_mermaid()`. Included so you can verify the
  polished diagram above isn't just illustrative — it's the actual
  structure LangGraph compiled. Regenerate it any time with:

  ```bash
  python3 -c "from matching_agent import build_graph; print(build_graph().get_graph().draw_mermaid())"
  ```

Both render natively on GitHub (paste the contents into a ```mermaid code
fence) or at https://mermaid.live.
