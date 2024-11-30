from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, ValidationError
import os
import google.generativeai as genai
from typing import List, Optional
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")
# print(google_api_key)
# configure Gemini API
genai.configure(api_key=google_api_key)


class InputText(BaseModel):
    text: str = Field(..., description="Input text to process", min_length=10)


class WordDetails(BaseModel):
    word: str = Field(..., description="The word being described.")
    synonyms: List[str] = Field(
        default_factory=list, description="List of synonyms for the word."
    )
    antonyms: List[str] = Field(
        default_factory=list, description="List of antonyms for the word."
    )
    usecase: Optional[str] = Field(
        None, description="An example use-case or definition of the word."
    )
    example: Optional[str] = Field(
        None, description="An example sentence using the word."
    )


class ProcessedResponse(BaseModel):
    difficult_words: List[WordDetails] = Field(
        ...,
        description="List of words with difficulty in vocabulary, grammar, and writing.",
    )
    medium_words: List[WordDetails] = Field(
        ...,
        description="List of words with medium difficulty in vocabulary, grammar, and writing.",
    )


# setup FastAPI app
app = FastAPI()

# Gemini Model app
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,  # type: ignore
    system_instruction="You are a helpful assistant who help reader to become better at vocabulary ,grammar and writing. Extract important and medium to hard difficult vocabulary words from the given text and produce their synonyms, antonyms, important use-cases, and example sentences in JSON format.",
)


# Mock processing function
def mock_process_text(input_text: str) -> dict:
    """
    A mock function to simulate processing.
    Replace with actual processing logic connected to Gemini API.
    """
    return {
        "difficult_words": [
            {
                "word": "satisfactory",
                "synonyms": ["acceptable", "adequate", "sufficient", "pleasing"],
                "antonyms": [
                    "unsatisfactory",
                    "inadequate",
                    "deficient",
                    "unsatisfying",
                ],
                "usecase": "Meeting or exceeding expectations; good enough.",
                "example": "The explanation was not satisfactory.",
            },
            # Add more word details as required
        ]
    }


def process_with_gemini(input_text: str) -> dict:
    try:
        chat_session = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                        "Mrs. Bennet, however, with the assistance of her five daughters, could ask on the subject, was sufficient to draw from her husband any satisfactory description of Mr. Bingley. They attacked him in various ways, with barefaced questions, ",
                        input_text,
                    ],
                },
                {
                    "role": "model",
                    "parts": [
                        '```json\n{\n  "difficult_words": [\n    {\n      "word": "elude",\n      "synonyms": ["evade", "avoid", "escape", "dodge"],\n      "antonyms": ["confront", "face", "encounter"],\n      "usecase": "To cleverly avoid something or someone.",\n      "example": "The thief managed to elude the police."\n    },```'
                    ],
                },
            ]
        )
        response = chat_session.send_message(input_text)
        return {response: response.text}
    except Exception as e:
        logger.error(f"Error while processing text: {e}")
        raise HTTPException(
            status_code=500, detail="Internal Server Error while processing text"
        )


@app.get("/")
async def root():
    return {"message": "Hello World"}


# Define the endpoint
@app.post("/process-text/", response_model=ProcessedResponse)
def process_text(input_text: InputText = Query(..., description="Input text")):
    """
    Process the input text using Gemini API and return structured JSON response.
    """
    try:
        response_text = process_with_gemini(input_text.text)
        # parse the response into Pydantic model
        parsed_response = ProcessedResponse.model_validate(response_text["response"])
        return parsed_response
    except ValidationError as ve:
        logger.error(f"Validation error: {ve}")
        raise HTTPException(
            status_code=422,
            detail="Invalid response format from Gemini API. Please check the API response.",
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error Error occured")


# Define GET endpoint with query parameters
@app.get("/process-text/", response_model=ProcessedResponse)
def process_text_get(
    input_text: str = Query(
        ..., description="The input text to process", min_length=10
    ),
):
    """
    Process the input text using Gemini API and return structured JSON response via GET request.
    """
    try:
        response_text = process_with_gemini(input_text)
        # Parse the response into Pydantic models
        parsed_response = ProcessedResponse.model_validate_json(
            response_text["response"]
        )
        return parsed_response
    except ValidationError as ve:
        logger.error(f"Validation error: {ve}")
        raise HTTPException(
            status_code=422, detail="Invalid response format from Gemini API"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
