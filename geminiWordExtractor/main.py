import os
import logging
from typing import List, Optional

import google.generativeai as genai
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, ValidationError, model_validator
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")


class InputText(BaseModel):
    """Pydantic model for input text validation."""

    text: str = Field(
        ..., min_length=10, max_length=10000, description="Input text to process"
    )

    @model_validator(mode="after")
    def validate_text_content(self):
        """Additional text content validation."""
        if not self.text.strip():
            raise ValueError("Input text cannot be empty or contain only whitespace")
        return self


class WordDetails(BaseModel):
    """Detailed model for word information."""

    word: str = Field(..., min_length=1, description="The word being described")
    synonyms: List[str] = Field(
        default_factory=list, description="List of synonyms for the word"
    )
    antonyms: List[str] = Field(
        default_factory=list, description="List of antonyms for the word"
    )
    usecase: Optional[str] = Field(
        None, max_length=300, description="Example use-case or definition"
    )
    example: Optional[str] = Field(
        None, max_length=300, description="Example sentence using the word"
    )


class ProcessedResponse(BaseModel):
    """Response model for processed text."""

    difficult_words: List[WordDetails] = Field(
        default_factory=list, description="List of difficult words"
    )
    medium_words: List[WordDetails] = Field(
        default_factory=list, description="List of medium difficulty words"
    )


class GeminiTextProcessor:
    """Centralized class for text processing with Gemini API."""

    def __init__(self):
        """Initialize Gemini API configuration."""
        self._api_key = google_api_key
        if not self._api_key:
            raise ValueError("Google API key is missing. Please set GOOGLE_API_KEY.")

        genai.configure(api_key=self._api_key)

        self._generation_config = {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "max_output_tokens": 2048,
        }

        self._model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=self._generation_config,  # type: ignore
            system_instruction="You are a helpful assistant who help reader to become better at vocabulary ,grammar and writing. Extract important and medium to hard difficult vocabulary words from the given text and produce their synonyms, antonyms, important use-cases, and example sentences in JSON format.",
        )

    def process_text(self, input_text: str) -> ProcessedResponse:
        """
        Process input text using Gemini API.

        Args:
            input_text (str): Text to analyze

        Returns:
            ProcessedResponse: Processed vocabulary details
        """
        try:
            # Ensure input is valid
            if not input_text or len(input_text.strip()) < 10:
                raise ValueError("Input text is too short")

            # Start chat session with context
            chat_session = self._model.start_chat(history=[])

            # Prompt for structured vocabulary extraction
            prompt = (
                f"Analyze the vocabulary in this text and extract words of difficulty. "
                f"Provide a JSON response with 'difficult_words' and 'medium_words'. "
                f"Text: {input_text}"
            )

            response = chat_session.send_message(prompt)

            # Basic parsing and validation
            try:
                parsed_response = ProcessedResponse.model_validate_json(response.text)
                return parsed_response
            except ValidationError as ve:
                logger.error(f"JSON Parsing Error: {ve}")
                raise HTTPException(
                    status_code=422, detail="Invalid response format from Gemini API"
                )

        except Exception as e:
            logger.exception(f"Text processing error: {e}")
            raise HTTPException(
                status_code=500, detail=f"Internal processing error: {str(e)}"
            )


# FastAPI Application Setup
app = FastAPI(
    title="Vocabulary Analysis API",
    description="Analyze text vocabulary using Google Gemini",
)

# Initialize processor
text_processor = GeminiTextProcessor()


@app.post("/process-text", response_model=ProcessedResponse)
async def process_text_endpoint(input_data: InputText):
    """
    Process input text and return vocabulary analysis.

    Args:
        input_data (InputText): Input text for analysis

    Returns:
        ProcessedResponse: Analyzed vocabulary details
    """
    return text_processor.process_text(input_data.text)


@app.get("/process-text", response_model=ProcessedResponse)
async def process_text_get_endpoint(
    input_text: str = Query(..., min_length=10, max_length=10000),
):
    """
    GET endpoint for text processing.

    Args:
        input_text (str): Text to analyze via query parameter

    Returns:
        ProcessedResponse: Analyzed vocabulary details
    """
    return text_processor.process_text(input_text)


@app.get("/")
async def root():
    """Root endpoint with basic API information."""
    return {
        "message": "Vocabulary Analysis API",
        "endpoints": ["/process-text (POST/GET)"],
    }


# Error Handling
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    logger.error(f"HTTP Error: {exc.detail}")
    return {"error": exc.detail, "status_code": exc.status_code}
