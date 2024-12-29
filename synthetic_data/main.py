from pydantic import BaseModel, Field, ValidationError
from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from typing import List
import json
import uuid
import re
from pathlib import Path
from time import sleep


# Step 1: Define the enhanced data schema
class EnglishQuestion(BaseModel):
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the question",
    )
    category: str = Field(..., description="Question Type")
    question: str = Field(..., description="The English language question")
    answer: str = Field(..., description="The correct answer to the question")
    thought_process: str = Field(
        ..., description="Explanation of the reasoning process to arrive at the answer"
    )


class QuestionGenerator:
    def __init__(self, model_name: str, output_file: Path):
        self.llm = OllamaLLM(model=model_name)
        self.prompt_template = PromptTemplate(
            input_variables=["category"],
            template="""
            Generate an English language question that tests understanding and usage.
            Focus on {category}.Question will be like fill in the blanks,One liner and mut not be MCQ type. write Output in this strict JSON format:

            {{
                "question": "<your specific question>",
                "answer": "<the correct answer>",
                "thought_process": "<Explain reasoning to arrive at the answer>"
            }}

            Do not include any text outside of the JSON object.
            """,
        )
        self.output_file = output_file
        self.output_file.touch(exist_ok=True)

    def clean_json_string(self, text: str) -> str:
        """Improved version to handle malformed or incomplete JSON."""
        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1:
            raise ValueError(f"No JSON object found. Response was: {text}")

        json_str = text[start : end + 1]

        # Remove any special characters that might break JSON parsing
        json_str = json_str.replace("\n", " ").replace("\r", " ")
        json_str = re.sub(r"[^\x20-\x7E]", "", json_str)

        # Fix common JSON formatting issues
        json_str = re.sub(
            r'(?<!\\)"([^"]*?)(?<!\\)":', r'"\1":', json_str
        )  # Fix key formatting
        json_str = re.sub(
            r':\s*"([^"]*?)(?<!\\)"(?=\s*[,}])', r': "\1"', json_str
        )  # Fix value formatting

        return json_str

    def parse_response(self, result: str) -> EnglishQuestion:
        """Parse the LLM response and validate it against the schema."""
        cleaned_json = self.clean_json_string(result)
        parsed_result = json.loads(cleaned_json)
        return EnglishQuestion(**parsed_result)

    def save_to_json(self, question: EnglishQuestion):
        """Save a validated question to the JSON file."""
        try:
            existing_data = self.load_existing_data()
            existing_data.append(question.model_dump())
            with open(self.output_file, "w") as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving to JSON: {e}")

    def load_existing_data(self) -> List[dict]:
        """Load existing questions from the JSON file."""
        try:
            with open(self.output_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    # def generate_question(self, category: str) -> EnglishQuestion:
    #     """Generate a single question for a given category."""
    #     result = self.prompt_template | self.llm
    #     response = result.invoke(input={"category": category})
    #     return self.parse_response(response)

    def generate_with_retries(self, category: str, retries: int = 3) -> EnglishQuestion:
        for attempt in range(retries):
            try:
                result = self.prompt_template | self.llm
                response = result.invoke(input={"category": category})
                return self.parse_response(response)
            except Exception as e:
                print(
                    f"Attempt {attempt + 1}/{retries} failed for category '{category}': {e}"
                )
                sleep(2)  # Small delay before retry
        raise ValueError(
            f"Failed to process category '{category}' after {retries} attempts."
        )

    def generate_questions(
        self, categories: List[str], iterations: int
    ) -> List[EnglishQuestion]:
        """Generate multiple questions for a list of categories."""
        all_questions = []
        for _ in range(iterations):
            for category in categories:
                try:
                    question = self.generate_with_retries(category)
                    self.save_to_json(question)
                    all_questions.append(question)
                    print(f"Successfully generated question for category: {category}")
                except (ValidationError, ValueError) as e:
                    print(f"Error processing category '{category}': {e}")
        return all_questions


# Utility Function for Display
def display_questions(questions: List[EnglishQuestion]):
    print("\nGenerated English Questions:")
    for question in questions:
        print("\n---")
        print(f"ID: {question.id}")
        print(f"Question: {question.question}")
        print(f"Answer: {question.answer}")
        print(f"Thought Process: {question.thought_process}")


# Example usage
if __name__ == "__main__":
    OUTPUT_FILE = Path("english_QA_new.json")
    generator = QuestionGenerator(model_name="llama3.2", output_file=OUTPUT_FILE)

    categories = [
        "word usage",
        "Phrasal Ver",
        "vocabulary",
        "idioms",
    ]
    iterations = 2

    generated_questions = generator.generate_questions(categories, iterations)
    display_questions(generated_questions)
