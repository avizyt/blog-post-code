import re
from typing import Dict, Any, Optional


class StackAnalyzer:
    def __init__(self, code_structure: Dict[str, Any]):
        self.code_structure = code_structure

    def analyze_trace(self, trace: str) -> str:
        """Analyze a stack trace and provide context from the codebase."""
        error_info = self.extract_error_info(trace)
        if not error_info:
            return "Could not parse error trace"

        file_path = error_info["file"]
        line_no = error_info["line"]
        error_type = error_info["error_type"]
        error_msg = error_info["message"]

        file_info = self.code_structure.get(file_path)
        if not file_info:
            return f"Error occurred in {file_path} at line {line_no}, but file not found in indexed codebase"

        context = self.get_error_context(file_info["content"], line_no)
        return f"""
            Error Analysis:
            - File: {file_path}
            - Line: {line_no}
            - Type: {error_type}
            - Message: {error_msg}

            Code Context:
            {context}
        """

    def extract_error_info(self, trace: str) -> Optional[Dict[str, Any]]:
        """Extract error information from a Python stack trace."""
        lines = trace.strip().split("\n")
        if not lines:
            return None

        # Try to find the error type and message
        error_match = re.match(r"^([A-Za-z.]+Error): (.+)$", lines[-1])
        if not error_match:
            return None

        error_type = error_match.group(1)
        error_msg = error_match.group(2)

        # Find the last file reference in the stack trace
        for line in reversed(lines):
            file_match = re.search(r'File "([^"]+)", line (\d+)', line)
            if file_match:
                return {
                    "file": file_match.group(1),
                    "line": int(file_match.group(2)),
                    "error_type": error_type,
                    "message": error_msg,
                }
        return None

    def get_error_context(
        self, content: str, line_no: int, context_lines: int = 3
    ) -> str:
        """Get the code context around the error line."""
        lines = content.split("\n")
        start = max(0, line_no - context_lines - 1)
        end = min(len(lines), line_no + context_lines)

        context = []
        for i in range(start, end):
            prefix = "-> " if i == line_no - 1 else "   "
            context.append(f"{prefix}{i + 1}: {lines[i]}")
        return "\n".join(context)
