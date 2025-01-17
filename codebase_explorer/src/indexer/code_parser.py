import ast
import os
from typing import Dict, Any

def parse_codebase(directory: str) -> Dict[str, Any]:
    """Parse Python files in the directory and extract code structure."""
    code_structure = {}
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        content = f.read()
                        tree = ast.parse(content)
                        code_structure[file_path] = {
                            "definitions": extract_definitions(tree),
                            "content": content
                        }
                    except Exception as e:
                        print(f"Error parsing {file_path}: {e}")
    return code_structure

def extract_definitions(tree: ast.AST) -> Dict[str, list]:
    """Extract class and function definitions from AST."""
    definitions = {
        "classes": [],
        "functions": [],
        "imports": []
    }
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            definitions["classes"].append({
                "name": node.name,
                "lineno": node.lineno
            })
        elif isinstance(node, ast.FunctionDef):
            definitions["functions"].append({
                "name": node.name,
                "lineno": node.lineno
            })
        elif isinstance(node, ast.Import):
            for name in node.names:
                definitions["imports"].append(name.name)
    return definitions
