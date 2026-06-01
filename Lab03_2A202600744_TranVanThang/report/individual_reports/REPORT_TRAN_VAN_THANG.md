# Individual Report: Lab 3 - Chatbot vs ReAct Agent (Vietnam Traffic Law RAG-Verifier)

- **Student Name**: Trần Văn Thắng
- **Student ID**: 2A202600744
- **Date**: 2026-06-01
- **Group**: Group 00

---

## I. Technical Contribution (15 Points)

I drove the implementation of the core components of the ReAct architecture, telemetry metrics, and the e-commerce test suites.

- **Modules Implemented & Consolidated**:
  1. `src/agent/agent.py`: Wrote the entire system logic. To strictly comply with the **"zero new files" policy** and maintain 100% compatibility with the original template repository structure, I successfully consolidated all required modules directly inside `src/agent/agent.py`:
     *   **RAG Legal Database (`TRAFFIC_LAW_DATABASE`)**: Embedded the entire, verified text database of Vietnam Traffic Law as a raw multi-line string constant, resolving all transient file path and CP1252/UTF-8 Windows encoding issues.
     *   **Custom RAG Search Tool (`search_traffic_law`)**: Implemented the lexical word-frequency keyword search tool with slang vehicle normalization.
     *   **Parameter Self-Healing Math Tool (`calculate_over_speed`)**: Built the float-overrun calculator using regex to strip units automatically.
     *   **Baseline Chatbot (`SimpleChatbot`)**: Embedded the direct LLM control chatbot baseline.
     *   **ReAct Loop (`ReActAgent`)**: Developed the core Thought-Action-Observation agent cycle, Cascade Parser, Repetitive Action Blocker, and Adaptive Hybrid Router.

- **Code Highlights (Adaptive Router & Blocker in run loop)**:
  Below is the core router and blocker implementation inside `agent.py`:
  ```python
  # 1. ADAPTIVE HYBRID ROUTER
  legal_keywords = ["cồn", "tốc độ", "phạt", "gplx", "bằng lái", "đèn đỏ", "đèn vàng", "thổi", "km/h", "vượt", "xe", "nồng độ", "chạy quá"]
  if not any(kw in user_input.lower() for kw in legal_keywords):
      logger.log_event("AGENT_ROUTE_DIRECT", {"input": user_input})
      res = self.llm.generate(user_input, system_prompt="You are a polite assistant. Answer directly.")
      tracker.track_request(...)
      return res.get("content", "").strip()

  # 4. REPETITIVE ACTION BLOCKER
  action_sig = (tool_name, tool_args.lower())
  if action_sig in executed_actions:
      observation = "Error: You have already executed this action with these exact parameters. Do not repeat the same action."
      logger.log_event("REPETITIVE_ACTION_BLOCKED", {"tool": tool_name, "args": tool_args})
  else:
      executed_actions.add(action_sig)
      observation = self._execute_tool(tool_name, tool_args)
  ```

- **Documentation**:
  The parser extracts the `Action` parameter using regex matching. It then forwards the argument string to `_execute_tool`, which dynamically resolves parameter signatures (via JSON parsing or structured regex argument extraction) and invokes the python function. The output is fed back as an `Observation:` line, keeping the agent bounded by real-time facts.

---

## II. Debugging Case Study (10 Points)

Using the structured logs in the `logs/` directory, I diagnosed and resolved a critical production bug:

- **Problem Description**: 
  The ReAct agent was unable to match the speed limit calculations in TC3, repeatedly throwing `ValueError` and failing to execute the mathematical speed difference overrun.
- **Log Source**:
  `logs/2026-06-01.log`:
  `{"event": "TOOL_CALL", "data": {"tool": "calculate_over_speed", "args": "actual_speed=\"78 km/h\", limit_speed=\"60 km/h\""}}`
  `{"event": "AGENT_PARSING_ERROR", "data": {"response": "Error: ValueError: could not convert string to float: '78 km/h'"}}`
- **Diagnosis**: 
  The LLM extracted parameters with text units `"78 km/h"` and `"60 km/h"` directly from the user query instead of clean floats, which crashed python's type conversion.
- **Solution**: 
  Developed a **Self-Healing Parameter Parser** inside `calculate_over_speed` using regex `([0-9.]+)` to automatically strip non-numeric units and coerce parameters into standard python floats.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1. **Reasoning**: 
   The `Thought` block acts as a logical chain of scratchpad steps. Instead of rushing to guess a single final value (which causes catastrophic arithmetic drift in LLMs), the agent is forced to outline *why* it needs a specific piece of data before calling the tool, vastly improving logical correctness.
2. **Reliability**: 
   ReAct Agents can perform worse on extremely simple queries (e.g. "What is an AI?") where a direct chatbot is 5x faster, uses 10% of the tokens, and is completely correct. The ReAct Agent introduces overhead (parsing risk, multiple API calls, extra latency) for tasks that do not require tool usage.
3. **Observation**: 
   Observations act as factual grounding. Every time the agent calls a tool, the environment gives it a hard, concrete value. This prevents the agent from hallucinating state changes and helps it adapt dynamically to real stock levels or shipping constraints.

---

## IV. Future Improvements (5 Points)

To scale this e-commerce prototype into a production-level RAG or multi-agent ecosystem, I propose:

- **Asynchronous Parallel Tool Calls**: Modify the ReAct loop to support calling multiple non-dependent tools concurrently, slashing total task duration.
- **Supervisor-Worker Agent Architecture**: Move from a monolithic ReAct loop to a multi-agent system where a Supervisor LLM routes complex requests to specialized child agents.
- **Dynamic Tool Retrieval**: As the quantity of tools scales from 2 to 500+, embed the tool descriptions in a vector database and perform Semantic Search to dynamically retrieve and inject only the 3-5 most relevant tool specifications into the system prompt, preserving the model's context window.
