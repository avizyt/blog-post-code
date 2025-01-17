import os
import json
import typer
from pathlib import Path

from typing import Optional
from indexer.code_parser import parse_codebase
from query_engine.query_processor import QueryProcessor
# from debugger.stack_analyzer import StackAnalyzer

app = typer.Typer()
query_processor = QueryProcessor()
# stack_analyzer: Optional[StackAnalyzer] = None


# def load_analyzer():
#     """Load the stack analyzer with the saved context."""
#     global stack_analyzer
#     if os.path.exists(query_processor.index_file):
#         try:
#             with open(query_processor.index_file, "r", encoding="utf-8") as f:
#                 code_structure = json.load(f)
#                 stack_analyzer = StackAnalyzer(code_structure)
#         except Exception as e:
#             typer.echo(f"Error loading analyzer: {e}")


@app.command()
def index(directory: str):
    """Index a Python codebase for querying and analysis."""
    # global stack_analyzer

    dir_path = Path(directory)
    if not dir_path.exists():
        typer.echo(f"Error: Directory '{directory}' does not exist")
        raise typer.Exit(1)

    typer.echo("Indexing codebase...")
    try:
        code_structure = parse_codebase(directory)
        query_processor.set_context(code_structure)
        # stack_analyzer = StackAnalyzer(code_structure)
        typer.echo(f"Successfully indexed {len(code_structure)} Python files")
    except Exception as e:
        typer.echo(f"Error indexing codebase: {e}")
        raise typer.Exit(1)


@app.command()
def query(query_text: str):
    """Query the indexed codebase using natural language."""
    if not query_processor.codebase_context:
        query_processor.load_context()

    response = query_processor.query(query_text)
    if response:
        typer.echo(response)
    else:
        typer.echo("Error: Failed to process query")
        raise typer.Exit(1)


# @app.command()
# def debug(trace_file: str):
#     """Analyze a Python stack trace file."""
#     if not stack_analyzer:
#         load_analyzer()
#         if not stack_analyzer:
#             typer.echo("Error: Please index a codebase first using the 'index' command")
#             raise typer.Exit(1)

#     try:
#         with open(trace_file, "r") as f:
#             trace = f.read()
#         analysis = stack_analyzer.analyze_trace(trace)
#         typer.echo(analysis)
#     except FileNotFoundError:
#         typer.echo(f"Error: Trace file '{trace_file}' not found")
#         raise typer.Exit(1)
#     except Exception as e:
#         typer.echo(f"Error analyzing stack trace: {e}")
#         raise typer.Exit(1)


if __name__ == "__main__":
    app()
