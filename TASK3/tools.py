import ast
import math
import operator
from pathlib import Path

from langchain_core.tools import tool

from config import DATA_DIR


# ==========================================================
# TOOL 1: REAL-TIME WEB SEARCH
# ==========================================================

@tool
def web_search(query: str) -> str:
    """
    Search the web using DuckDuckGo.

    Use this tool to find recent information, facts,
    research material, statistics, and information
    that is not already available in local files.

    Args:
        query: The search query.
    """

    from langchain_community.tools import DuckDuckGoSearchRun

    try:
        search = DuckDuckGoSearchRun()
        result = search.invoke(query)

        return str(result)[:12000]

    except Exception as exc:
        return (
            f"Web search failed: {type(exc).__name__}: {exc}. "
            "Try a different query or another source."
        )


# ==========================================================
# TOOL 2: PYTHON MATHEMATICAL CALCULATOR
# ==========================================================

_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

_ALLOWED_FUNCTIONS = {
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "log10": math.log10,
    "exp": math.exp,
    "ceil": math.ceil,
    "floor": math.floor,
    "fabs": math.fabs,
}

_ALLOWED_CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
}


def _safe_evaluate(node, depth=0):
    """Evaluate a restricted mathematical expression."""

    if depth > 30:
        raise ValueError("Expression is too deeply nested.")

    if isinstance(node, ast.Constant):
        if (
            isinstance(node.value, bool)
            or not isinstance(node.value, (int, float))
        ):
            raise ValueError("Only numeric constants are allowed.")

        if abs(node.value) > 1e100:
            raise ValueError("Number is too large.")

        return node.value

    if isinstance(node, ast.BinOp):
        operator_type = type(node.op)

        if operator_type not in _ALLOWED_OPERATORS:
            raise ValueError("Unsupported mathematical operator.")

        left = _safe_evaluate(node.left, depth + 1)
        right = _safe_evaluate(node.right, depth + 1)

        if isinstance(node.op, ast.Pow):
            if abs(right) > 1000:
                raise ValueError("Exponent is too large.")

            if abs(left) > 1e100:
                raise ValueError("Base is too large.")

        result = _ALLOWED_OPERATORS[operator_type](left, right)

        if isinstance(result, (int, float)):
            if abs(result) > 1e100:
                raise ValueError("Result is too large.")

        return result

    if isinstance(node, ast.UnaryOp):
        operator_type = type(node.op)

        if operator_type not in _ALLOWED_OPERATORS:
            raise ValueError("Unsupported unary operator.")

        value = _safe_evaluate(node.operand, depth + 1)

        return _ALLOWED_OPERATORS[operator_type](value)

    if isinstance(node, ast.Name):
        if node.id not in _ALLOWED_CONSTANTS:
            raise ValueError(f"Unknown constant: {node.id}")

        return _ALLOWED_CONSTANTS[node.id]

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Unsupported function.")

        function_name = node.func.id

        if function_name not in _ALLOWED_FUNCTIONS:
            raise ValueError(
                f"Function '{function_name}' is not allowed."
            )

        if node.keywords:
            raise ValueError("Keyword arguments are not allowed.")

        arguments = [
            _safe_evaluate(arg, depth + 1)
            for arg in node.args
        ]

        return _ALLOWED_FUNCTIONS[function_name](*arguments)

    raise ValueError("Unsupported expression.")


@tool
def calculator(expression: str) -> str:
    """
    Calculate mathematical expressions accurately using Python.

    Use for arithmetic, percentages, averages, powers,
    square roots, logarithms, and trigonometric calculations.

    Examples:
        (125 * 4) + 80
        15 / 100 * 2500
        sqrt(144)
        log10(1000)
        pi * 5 ** 2

    Args:
        expression: A mathematical expression, not a natural
                    language question.
    """

    try:
        if len(expression) > 500:
            return "Error: Expression is too long."

        tree = ast.parse(expression, mode="eval")

        result = _safe_evaluate(tree.body)

        if isinstance(result, float) and not math.isfinite(result):
            return "Error: Result is not finite."

        return f"Expression: {expression}\nResult: {result}"

    except Exception as exc:
        return f"Calculation error: {exc}"


# ==========================================================
# TOOL 3: LOCAL FILE READER
# ==========================================================

@tool
def read_local_file(filename: str) -> str:
    """
    Read a local text file from the project's data directory.

    Use this tool when the user asks about information
    contained in uploaded notes, research documents,
    or local text files.

    Pass a filename relative to the data directory,
    such as research_notes.txt.

    Only text-based files within the allowed data directory
    can be read.

    Args:
        filename: The relative filename to read.
    """

    try:
        requested_path = Path(filename)

        # Disallow absolute paths.
        if requested_path.is_absolute():
            return "Error: Absolute paths are not allowed."

        # Resolve and validate the target path.
        target = (DATA_DIR / requested_path).resolve()

        if not target.is_relative_to(DATA_DIR):
            return "Error: Access outside the data directory is forbidden."

        if target.suffix.lower() not in {
            ".txt",
            ".md",
            ".csv",
            ".json",
            ".log",
        }:
            return (
                "Error: Unsupported file type. "
                "Use .txt, .md, .csv, .json, or .log."
            )

        if not target.exists():
            return f"Error: File '{filename}' does not exist."

        if not target.is_file():
            return "Error: The requested path is not a file."

        # Avoid loading very large files into the model context.
        max_bytes = 100_000

        with target.open("rb") as file:
            raw_content = file.read(max_bytes + 1)

        truncated = len(raw_content) > max_bytes
        content = raw_content[:max_bytes].decode(
            "utf-8",
            errors="replace"
        )

        if truncated:
            content += "\n\n[File truncated at 100 KB.]"

        if not content.strip():
            return f"The file '{filename}' is empty."

        return (
            f"File: {filename}\n"
            f"Content:\n{content}"
        )

    except Exception as exc:
        return f"File reading error: {exc}"


# ==========================================================
# EXPORT ALL AVAILABLE TOOLS
# ==========================================================

TOOLS = [
    web_search,
    calculator,
    read_local_file,
]