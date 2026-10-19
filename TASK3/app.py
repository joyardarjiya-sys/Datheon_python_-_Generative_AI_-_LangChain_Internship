
import streamlit as st
import contextlib
import io
import re
import threading
from datetime import datetime

from agent import create_research_agent, run_agent

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Autonomous AI Research Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------
# STYLING
# --------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

.stApp {
    background:
        radial-gradient(ellipse at 10% 0%, rgba(93, 45, 160, 0.18), transparent 40%),
        radial-gradient(ellipse at 100% 20%, rgba(0, 210, 255, 0.08), transparent 35%),
        #080b14;
    color: #e8eaf3;
    font-family: 'Inter', sans-serif;
}

header[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    padding-top: 1.5rem;
    max-width: 1250px;
}

.agent-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
    padding: 22px 26px;
    margin-bottom: 25px;
    border: 1px solid rgba(151, 112, 255, 0.3);
    border-radius: 18px;
    background: rgba(18, 21, 38, 0.88);
    box-shadow: 0 0 35px rgba(112, 66, 255, 0.08);
}

.brand {
    font-size: 24px;
    font-weight: 800;
    letter-spacing: -0.8px;
}

.brand span {
    color: #b59aff;
}

.subtitle {
    color: #8d96ad;
    font-size: 12px;
    margin-top: 6px;
}

.clock {
    text-align: right;
    color: #b6c1d9;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    line-height: 1.8;
}

.section-title {
    font-size: 15px;
    font-weight: 700;
    color: #d8dafa;
    margin: 12px 0;
}

.status-card {
    padding: 16px;
    background: rgba(21, 25, 43, 0.8);
    border: 1px solid #292d45;
    border-radius: 13px;
    margin-bottom: 12px;
}

.status-label {
    color: #929bb3;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1.3px;
}

.status-value {
    color: #c4b5fd;
    font-size: 15px;
    font-weight: 600;
    margin-top: 7px;
}

.log-card {
    background: rgba(12, 15, 27, 0.96);
    border: 1px solid #272b40;
    border-radius: 12px;
    padding: 15px 17px;
    margin: 12px 0;
}

.log-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    margin-bottom: 9px;
    color: #b59aff;
}

.log-body {
    color: #c5cce0;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    line-height: 1.8;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
}

.final-card {
    background: linear-gradient(
        135deg,
        rgba(72, 40, 130, 0.22),
        rgba(13, 22, 39, 0.95)
    );
    border: 1px solid rgba(151, 112, 255, 0.45);
    border-radius: 16px;
    padding: 22px;
    margin-top: 15px;
}

.final-title {
    color: #c4b5fd;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 1.5px;
    margin-bottom: 14px;
}

div[data-testid="stChatMessage"] {
    background: rgba(18, 21, 38, 0.7);
    border: 1px solid #252a40;
    border-radius: 14px;
}

.stTextArea textarea {
    background: #101426;
    color: #e8eaf3;
    border: 1px solid #383454;
    border-radius: 12px;
}

.stButton button {
    border-radius: 10px;
    font-weight: 600;
}

div[data-testid="stSidebar"] {
    background: #0c0f1c;
    border-right: 1px solid #272b40;
}

.small-note {
    color: #778199;
    font-size: 11px;
    line-height: 1.8;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

now = datetime.now()

st.markdown(f"""
<div class="agent-header">
    <div>
        <div class="brand">⚡ Autonomous <span>AI Agent</span></div>
        <div class="subtitle">
            MULTI-STEP REASONING · TOOL EXECUTION · RESEARCH
        </div>
    </div>
    <div class="clock">
        <div>{now.strftime("%d %b %Y")}</div>
        <div>{now.strftime("%I:%M:%S %p")}</div>
        <div>LOCAL SYSTEM TIME</div>
    </div>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "agent" not in st.session_state:
    st.session_state.agent = None

if "history" not in st.session_state:
    st.session_state.history = []

if "logs" not in st.session_state:
    st.session_state.logs = []

if "final_answer" not in st.session_state:
    st.session_state.final_answer = ""

if "last_error" not in st.session_state:
    st.session_state.last_error = ""

if "run_count" not in st.session_state:
    st.session_state.run_count = 0


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.markdown("## ⚙️ Agent Console")
    st.caption("AUTONOMOUS RESEARCH SYSTEM")

    st.markdown("---")

    st.markdown("### Available Tools")

    st.markdown("""
    <div class="status-card">
        <div class="status-label">Tool 01</div>
        <div class="status-value">🔎 Web Search</div>
        <div class="small-note">DuckDuckGo research</div>
    </div>

    <div class="status-card">
        <div class="status-label">Tool 02</div>
        <div class="status-value">🧮 Calculator</div>
        <div class="small-note">Mathematical expressions</div>
    </div>

    <div class="status-card">
        <div class="status-label">Tool 03</div>
        <div class="status-value">📄 Local File Reader</div>
        <div class="small-note">Read permitted files from data/</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### Session Statistics")
    st.metric("Queries submitted", st.session_state.run_count)

    if st.button("🗑️ Clear session", use_container_width=True):
        st.session_state.history = []
        st.session_state.logs = []
        st.session_state.final_answer = ""
        st.session_state.last_error = ""
        st.session_state.run_count = 0
        st.rerun()

    st.markdown("---")
    st.markdown(
        '<div class="small-note">Powered by Python · LangChain · Gemini</div>',
        unsafe_allow_html=True,
    )


# --------------------------------------------------
# INITIALIZE AGENT
# --------------------------------------------------

if st.session_state.agent is None:
    with st.spinner("Initializing the AI agent..."):
        try:
            st.session_state.agent = create_research_agent()
            st.session_state.last_error = ""
        except Exception as exc:
            st.session_state.last_error = (
                f"Agent initialization failed: {type(exc).__name__}: {exc}"
            )


# --------------------------------------------------
# DASHBOARD STATUS
# --------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="status-card">
        <div class="status-label">Agent Status</div>
        <div class="status-value">● Ready</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="status-card">
        <div class="status-label">Execution Mode</div>
        <div class="status-value">Tool-enabled Agent</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="status-card">
        <div class="status-label">Interface</div>
        <div class="status-value">Web Console</div>
    </div>
    """, unsafe_allow_html=True)


# --------------------------------------------------
# QUERY INPUT
# --------------------------------------------------

st.markdown("## 💬 Ask your research agent")
st.caption(
    "Enter a question or a multi-step task. "
    "The agent will select tools and return its response."
)

with st.form("query_form", clear_on_submit=True):
    question = st.text_area(
        "Your query",
        placeholder=(
            "Example: Search for three benefits of AI in education, "
            "read research_notes.txt, and calculate the total profit "
            "and ROI using the values in that file."
        ),
        height=110,
        label_visibility="collapsed",
    )

    submitted = st.form_submit_button(
        "⚡ Run Agent",
        type="primary",
        use_container_width=True,
    )


# --------------------------------------------------
# RUN AGENT AND CAPTURE EXISTING CONSOLE OUTPUT
# --------------------------------------------------

if submitted:
    if not question.strip():
        st.warning("Please enter a question first.")

    elif st.session_state.agent is None:
        st.error(
            st.session_state.last_error
            or "The agent could not initialize. Check your configuration."
        )

    else:
        st.session_state.run_count += 1
        st.session_state.logs = []
        st.session_state.final_answer = ""
        st.session_state.last_error = ""

        output_buffer = io.StringIO()

        with st.status(
            "Agent is processing your query...",
            expanded=True,
        ) as status:
            st.write("Sending query to the existing LangChain agent...")

            try:
                # Capture the terminal-style output from the existing run_agent.
                # Redirect both output streams so diagnostics are retained.
                with contextlib.redirect_stdout(output_buffer), \
                     contextlib.redirect_stderr(output_buffer):
                    run_agent(st.session_state.agent, question.strip())

                captured_output = output_buffer.getvalue()

                # Parse the existing timestamped terminal log format.
                pattern = re.compile(
                    r"\[(\d{2}:\d{2}:\d{2})\]\s+\[([^\]]+)\]\s*\n(.*?)(?=\n\[\d{2}:\d{2}:\d{2}\]\s+\[|\Z)",
                    re.DOTALL,
                )

                for match in pattern.finditer(captured_output):
                    timestamp, label, body = match.groups()
                    st.session_state.logs.append({
                        "timestamp": timestamp,
                        "label": label.strip(),
                        "body": body.strip(),
                    })

                if not st.session_state.logs and captured_output.strip():
                    st.session_state.logs.append({
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                        "label": "AGENT OUTPUT",
                        "body": captured_output.strip(),
                    })

                # Extract final answer from the existing formatted output.
                for entry in reversed(st.session_state.logs):
                    if "FINAL ANSWER" in entry["label"].upper():
                        st.session_state.final_answer = entry["body"]
                        break

                if not st.session_state.final_answer:
                    for entry in reversed(st.session_state.logs):
                        if entry["label"].upper() == "ERROR":
                            st.session_state.last_error = entry["body"]
                            break

                st.session_state.history.append({
                    "question": question.strip(),
                    "answer": st.session_state.final_answer,
                    "logs": list(st.session_state.logs),
                })

                status.update(
                    label=(
                        "Agent execution completed"
                        if not st.session_state.last_error
                        else "Agent returned an error"
                    ),
                    state=(
                        "complete"
                        if not st.session_state.last_error
                        else "error"
                    ),
                    expanded=False,
                )

            except Exception as exc:
                st.session_state.last_error = (
                    f"{type(exc).__name__}: {exc}"
                )
                st.session_state.logs.append({
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "label": "ERROR",
                    "body": st.session_state.last_error,
                })
                status.update(
                    label="Agent execution failed",
                    state="error",
                    expanded=True,
                )


# --------------------------------------------------
# DISPLAY OUTPUT LIKE THE TERMINAL
# --------------------------------------------------

if st.session_state.history:
    latest = st.session_state.history[-1]

    st.markdown("---")
    st.markdown("## 📡 Execution Console")

    st.markdown(
        f"""
        <div class="log-card">
            <div class="log-label">USER QUERY</div>
            <div class="log-body">{latest["question"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for entry in latest["logs"]:
        label = entry["label"].upper()

        if "FINAL ANSWER" in label:
            continue

        if "ERROR" in label or "INITIALIZATION ERROR" in label:
            color = "#fb7185"
        elif "ACTION" in label:
            color = "#67e8f9"
        elif "OBSERVATION" in label:
            color = "#c4b5fd"
        else:
            color = "#b59aff"

        # Use Streamlit's escaped text renderer for log content.
        with st.container(border=True):
            st.markdown(
                f"<div class='log-label' style='color:{color}'>"
                f"{entry['timestamp']} · {label}</div>",
                unsafe_allow_html=True,
            )
            st.code(entry["body"], language=None)

    if latest["answer"]:
        st.markdown("""
        <div class="final-card">
            <div class="final-title">✦ FINAL ANSWER</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(latest["answer"])

    elif st.session_state.last_error:
        st.error(st.session_state.last_error)

    else:
        st.info(
            "The agent finished, but its final answer could not be "
            "extracted from the console output. Review the execution logs."
        )

else:
    st.markdown("---")
    st.markdown("### 🚀 Try a sample query")

    examples = [
        "Calculate the compound interest on 50000 at 8% annual interest for 3 years.",
        "Read research_notes.txt from the data directory and summarize its contents.",
        "Search for three benefits of AI in education.",
    ]

    for example in examples:
        st.markdown(f"- {example}")

    if st.session_state.last_error:
        st.error(st.session_state.last_error)


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown("---")
st.markdown(
    '<div class="small-note" style="text-align:center">'
    'AUTONOMOUS AI RESEARCH AGENT · LANGCHAIN TOOL EXECUTION CONSOLE'
    '</div>',
    unsafe_allow_html=True,
)
