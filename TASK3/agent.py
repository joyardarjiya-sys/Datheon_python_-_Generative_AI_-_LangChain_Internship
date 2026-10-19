#!/usr/bin/env python3
"""A small console research agent using OpenAI-compatible function calling.

The trace intentionally shows only tool actions and observations, not hidden
chain-of-thought. Configure OPENAI_API_KEY and optionally OPENAI_API_BASE.
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_agent

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    AGENT_MAX_ITERATIONS,
    validate_config,
)

from tools import TOOLS
from utils import (
    print_banner,
    print_event,
    print_final_answer,
)


SYSTEM_PROMPT = """
You are an autonomous AI research agent.

Your job is to solve multi-step problems by deciding
when to use the available tools.

AVAILABLE TOOLS:
1. web_search:
   Search DuckDuckGo for information from the web.
2. calculator:
   Calculate mathematical expressions using Python.
3. read_local_file:
   Read local text documents from the data directory.

OPERATING RULES:
- Understand the complete user request before acting.
- Break compound problems into manageable steps.
- Use tools when they improve factual accuracy.
- Use web_search for current or external information.
- Use calculator for calculations instead of guessing.
- Use read_local_file when the answer depends on local files.
- You may call multiple tools when necessary.
- Use the results returned by tools to guide subsequent actions.
- If a tool fails, consider a reasonable alternative.
- Never invent search results, file contents, or calculations.
- Clearly distinguish verified facts from estimates.
- If information is insufficient, say so.
- Provide a coherent final answer that addresses every part
  of the original question.
- Do not claim a tool was used unless it actually was.
- Do not expose private chain-of-thought.
  You may briefly explain your approach and summarize evidence.
"""


def create_research_agent():
    """Initialize the LLM and create the tool-calling agent."""

    validate_config()

    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        google_api_key=GEMINI_API_KEY,
        temperature=0,
        max_retries=2,
        timeout =20,
    )

    agent = create_agent(
        model=llm,
        tools=TOOLS,
        system_prompt=SYSTEM_PROMPT,
    )

    return agent


def run_agent(agent, question: str):
    """Run the agent on a user's question."""

    print_event("USER QUERY", question)

    try:
        result = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": question,
                    }
                ]
            },
            config={
                "recursion_limit": max(
                    10,
                    AGENT_MAX_ITERATIONS * 2 + 2
                )
            },
        )

        messages = result.get("messages", [])

        # Display actual tool calls and their observations.
        for message in messages:
            tool_calls = getattr(message, "tool_calls", None) or []

            for tool_call in tool_calls:
                tool_name = tool_call.get("name", "unknown")
                tool_args = tool_call.get("args", {})

                print_event(
                    "ACTION",
                    f"Tool selected: {tool_name}\n"
                    f"Input: {tool_args}",
                )

            # ToolMessage represents the output of a tool.
            if getattr(message, "type", "") == "tool":
                print_event(
                    "OBSERVATION",
                    str(message.content)[:3000],
                )

        # Find the last assistant response.
        final_answer = ""

        for message in reversed(messages):
            if getattr(message, "type", "") == "ai":
                if getattr(message, "tool_calls", None):
                    continue

                final_answer = message.content
                break

        if isinstance(final_answer, list):
            final_answer = "\n".join(
                str(item.get("text", item))
                if isinstance(item, dict)
                else str(item)
                for item in final_answer
            )

        if not final_answer:
            final_answer = (
                "The agent finished without producing "
                "a final text response."
            )

        print_final_answer(str(final_answer))

    except KeyboardInterrupt:
        print_event("INTERRUPTED", "The operation was cancelled.")

    except Exception as exc:
        print_event(
            "ERROR",
            f"{type(exc).__name__}: {exc}",
        )

        print(
            "\nCheck your API key, model availability, "
            "internet connection, and installed dependencies."
        )


def main():
    """Start the interactive console application."""

    print_banner()

    try:
        agent = create_research_agent()

    except Exception as exc:
        print_event(
            "INITIALIZATION ERROR",
            f"{type(exc).__name__}: {exc}",
        )
        return

    print("\nAgent initialized successfully.")
    print("Enter a compound question to begin.")
    print("Type 'exit' or 'quit' to stop.")

    while True:
        try:
            question = input("\nYou: ").strip()

            if question.lower() in {"exit", "quit"}:
                print("\nResearch session ended. Goodbye!")
                break

            if not question:
                continue

            run_agent(agent, question)

        except (KeyboardInterrupt, EOFError):
            print("\nResearch session ended. Goodbye!")
            break


if __name__ == "__main__":
    main()