import os
import json
# from llama_index.embeddings.gemini import GeminiEmbedding


from dotenv import load_dotenv
from typing import Dict, Any, Optional
from .gemini_client import GeminiClient

load_dotenv()

gemini_api_key = os.getenv("GOOGLE_API_KEY")
# model_name = "models/embeddings-001"
# embed_model = GeminiEmbedding(model_name=model_name, api_key=gemini_api_key)


class QueryProcessor:
    def __init__(self):
        self.gemini_client = GeminiClient()
        self.codebase_context: Optional[Dict[str, Any]] = None
        self.index_file = "./indexes/codebase_index.json"

    def load_context(self):
        """Load the codebase context from disk if it exists."""
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, "r", encoding="utf-8") as f:
                    self.codebase_context = json.load(f)
            except Exception as e:
                print(f"Error loading index: {e}")
                self.codebase_context = None

    def save_context(self):
        """Save the codebase context to disk."""
        if self.codebase_context:
            try:
                with open(self.index_file, "w", encoding="utf-8") as f:
                    json.dump(self.codebase_context, f, indent=2)
            except Exception as e:
                print(f"Error saving index: {e}")

    def set_context(self, context: Dict[str, Any]):
        """Set the codebase context for queries."""
        self.codebase_context = context
        self.save_context()

    def format_context(self) -> str:
        """Format the codebase context for Gemini."""
        if not self.codebase_context:
            return ""

        context_parts = []
        for file_path, details in self.codebase_context.items():
            defs = details["definitions"]
            content = details["content"]
            context_parts.append(
                f"File: {file_path}\n"
                f"Classes: {[c['name'] for c in defs['classes']]}\n"
                f"Functions: {[f['name'] for f in defs['functions']]}\n"
                f"Imports: {defs['imports']}\n"
                f"Content: {content}\n"
            )
        return "\n\n".join(context_parts)

    def query(self, query: str) -> Optional[str]:
        """Process a query about the codebase."""
        if not self.codebase_context:
            return (
                "Error: No codebase context available. Please index the codebase first."
            )

        prompt = f"""
        Given the following codebase structure:
        {self.format_context()}
        
        Query: {query}
        
        Please provide a detailed and accurate answer based on the codebase structure above.
        """
        return self.gemini_client.query(prompt)
