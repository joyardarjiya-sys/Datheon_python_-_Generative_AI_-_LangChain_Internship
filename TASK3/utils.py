from datetime import datetime


def print_banner():
    """Display the agent's startup banner."""

    print("\n" + "=" * 65)
    print("              AUTONOMOUS AI RESEARCH AGENT")
    print("=" * 65)
    print("LLM       : Google Gemini")
    print("Search    : DuckDuckGo")
    print("Calculator: Python")
    print("Files     : Local data directory")
    print("Started   :", datetime.now().strftime("%d-%m-%Y %I:%M:%S %p"))
    print("=" * 65)


def print_event(event_type: str, message: str):
    """Print a formatted agent event."""

    timestamp = datetime.now().strftime("%H:%M:%S")

    print(f"\n[{timestamp}] [{event_type}]")
    print(message)


def print_final_answer(answer: str):
    """Display the final answer."""

    print("\n" + "=" * 65)
    print("                       FINAL ANSWER")
    print("=" * 65)
    print(answer)
    print("=" * 65)