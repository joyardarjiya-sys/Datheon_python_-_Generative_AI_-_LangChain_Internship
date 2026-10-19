# TASK 3 — Autonomous AI Research Agent

## Overview

This project implements an autonomous, tool-calling AI agent that solves multi-step problems by combining a large language model with external tools.

The agent can decide when to search the web, perform calculations, or retrieve information from local documents.

## Features

* **Autonomous tool selection:** Chooses tools based on the user's request.
* **Web search:** Uses DuckDuckGo to retrieve relevant online information.
* **Python calculator:** Evaluates mathematical expressions using a restricted Python-based evaluator.
* **Local file reader:** Reads supported text-based files from the project's data directory.
* **Multi-step execution:** Uses tool outputs to guide subsequent actions.
* **Console interface:** Accepts interactive questions and displays tool actions and observations.
* **Environment-based configuration:** Loads API credentials from a local `.env` file.
* **Docker support:** Includes a Dockerfile for containerized execution.

## Technology Stack

* Python
* LangChain
* Google Gemini
* DuckDuckGo Search
* Python AST
* Docker

## Project Structure

```text
TASK3/
├── agent.py
├── tools.py
├── config.py
├── utils.py
├── requirements.txt
├── .env.example
├── .gitignore
├── Dockerfile
├── README.md
└── data/
    └── research_notes.txt
```

## Installation

1. Install Python 3.11 or a compatible supported version.
2. Clone the repository or navigate to the TASK3 directory.
3. Create and activate a virtual environment.
4. Install the dependencies.
5. Configure the Gemini API key.

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

Create a `.env` file using `.env.example` as a template and add your API key.

## Running the Agent

Run:

```bash
python agent.py
```

Enter a question when prompted.

Type `exit` or `quit` to close the application.

## Example Queries

**Web research and calculation**

"Search for recent information about renewable energy adoption in India and calculate the percentage increase if adoption rises from 20% to 28%."

**Local file retrieval and calculation**

"Read research_notes.txt and calculate the total profit over 12 months using the revenue and cost values."

**Compound research**

"Search for three common applications of machine learning, summarize them, and calculate the average of 75, 82, and 91."

## Security

* API credentials are stored in `.env`.
* The `.env` file must not be committed to GitHub.
* The calculator uses a restricted expression evaluator rather than unrestricted `eval()`.
* Local file access is restricted to the configured data directory.

## Expected Output

The console displays the user's question, selected tools, tool inputs, observations, and a final answer.

The exact tools and execution sequence depend on the problem.

## Learning Outcomes

This project demonstrates tool calling, agent orchestration, prompt design, environment configuration, safe mathematical evaluation, file access, and multi-step AI problem solving.
