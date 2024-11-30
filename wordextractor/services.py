import os
import json

import logging
from fastapi import HTTPException
import google.generativeai as genai
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


# Gemini API Service


class GeminiVocabularyService:
    def __init__(self):
        _google_api_key = os.getenv("GOOGLE_API_KEY")
        # Retrieve API Key
        self.api_key = _google_api_key
        if not self.api_key:
            raise ValueError(
                "Google API Key is missing. Please set GOOGLE_API_KEY in .env file."
            )

        # Configure Gemini API
        genai.configure(api_key=self.api_key)

        # Generation Configuration
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "max_output_tokens": 8192,
        }

        # Create Generative Model
        self.vocab_model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=self.generation_config,  # type: ignore
            system_instruction="""
            You are an expert vocabulary extractor. 
            For the given text:
            1. Identify 3-5 challenging vocabulary words
            2. Provide the following for EACH word in a STRICT JSON format:
            - word: The exact word
            - synonyms: List of 2-3 synonyms
            - antonyms: List of 2-3 antonyms
            - usecase: A brief explanation of the word's usage
            - example: An example sentence using the word

            IMPORTANT: Return ONLY a valid JSON that matches this structure:
            {
              "difficult_words": [
                {
                  "word": "string",
                  "synonyms": ["string1", "string2"],
                  "antonyms": ["string1", "string2"],
                  "usecase": "string",
                  "example": "string"
                }
              ],
              "medium_words": [
                {
                  "word": "string",
                  "synonyms": ["string1", "string2"],
                  "antonyms": ["string1", "string2"],
                  "usecase": "string",
                  "example": "string"
                }
              ],
            }
            """,
        )

    async def extract_vocabulary(self, text: str) -> dict:
        try:
            # Create a new chat session
            chat_session = self.vocab_model.start_chat(history=[])

            # Send message and await response
            response = await chat_session.send_message_async(text)

            # Extract and clean the text response
            response_text = response.text.strip()

            # Attempt to extract JSON
            return self._parse_response(response_text)

        except Exception as e:
            logger.error(f"Vocabulary extraction error: {str(e)}")
            logger.error(f"Full response: {response_text}")
            raise HTTPException(
                status_code=500, detail=f"Vocabulary extraction failed: {str(e)}"
            )

    def _parse_response(self, response_text: str) -> dict:
        # Remove markdown code blocks if present
        response_text = response_text.replace("```json", "").replace("```", "").strip()

        try:
            # Attempt to parse JSON
            parsed_data = json.loads(response_text)

            # Validate the structure
            if (
                not isinstance(parsed_data, dict)
                or "difficult_words" not in parsed_data
            ):
                raise ValueError("Invalid JSON structure")

            return parsed_data

        except json.JSONDecodeError as json_err:
            logger.error(f"JSON Decode Error: {json_err}")
            logger.error(f"Problematic response: {response_text}")
            raise HTTPException(
                status_code=400, detail="Invalid JSON response from Gemini"
            )
        except ValueError as val_err:
            logger.error(f"Validation Error: {val_err}")
            raise HTTPException(
                status_code=400, detail="Invalid vocabulary extraction response"
            )


class QuestionAnswerService:
    def __init__(self):
        _google_api_key = os.getenv("GOOGLE_API_KEY")
        # Retrieve API Key
        self.api_key = _google_api_key
        if not self.api_key:
            raise ValueError(
                "Google API Key is missing. Please set GOOGLE_API_KEY in .env file."
            )

        # Configure Gemini API
        genai.configure(api_key=self.api_key)

        # Generation Configuration
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "max_output_tokens": 8192,
        }

        self.qa_model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=self.generation_config,  # type: ignore
            system_instruction="""
            You are an expert at creating comprehensive comprehension questions and answers.
            For the given text:
            1. Generate 8-10 diverse questions covering:
               - Vocabulary meaning
               - Literary devices
               - Grammatical analysis
               - Thematic insights
               - Contextual understanding

            IMPORTANT: Return ONLY a valid JSON in this EXACT format:
            {
              "questions_and_answers": [
                {
                  "question": "string",
                  "answer": "string"
                }
              ]
            }

            Guidelines:
            - Questions should be clear and specific
            - Answers should be concise and accurate
            - Cover different levels of comprehension
            - Avoid yes/no questions
            """,
        )

    async def extract_questions_and_answers(self, text: str) -> dict:
        """
        Extracts questions and answers from the given text using the provided model.
        """
        try:
            # Create a new chat session
            chat_session = self.qa_model.start_chat(history=[])

            full_prompt = f"""
            Analyze the following text and generate comprehensive comprehension questions and answers:

            {text}

            Ensure the questions and answers provide deep insights into the text's meaning, style, and context.
            """

            # Send message and await response
            response = await chat_session.send_message_async(full_prompt)

            # Extract and clean the text response
            response_text = response.text.strip()

            # Attempt to parse and validate the response
            return self._parse_response(response_text)

        except Exception as e:
            logger.error(f"Question and answer extraction error: {str(e)}")
            logger.error(f"Full response: {response_text}")
            raise HTTPException(
                status_code=500, detail=f"Question-answer extraction failed: {str(e)}"
            )

    def _parse_response(self, response_text: str) -> dict:
        """
        Parses and validates the JSON response from the model.
        """
        # Remove markdown code blocks if present
        response_text = response_text.replace("```json", "").replace("```", "").strip()

        try:
            # Attempt to parse JSON
            parsed_data = json.loads(response_text)

            # Validate the structure
            if (
                not isinstance(parsed_data, dict)
                or "questions_and_answers" not in parsed_data
            ):
                raise ValueError("Response must be a list of questions and answers.")

            return parsed_data

        except json.JSONDecodeError as json_err:
            logger.error(f"JSON Decode Error: {json_err}")
            logger.error(f"Problematic response: {response_text}")
            raise HTTPException(
                status_code=400, detail="Invalid JSON response from the model"
            )
        except ValueError as val_err:
            logger.error(f"Validation Error: {val_err}")
            raise HTTPException(
                status_code=400, detail="Invalid question-answer extraction response"
            )
