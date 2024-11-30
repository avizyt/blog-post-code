from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from .models import VocabularyResponse, QuestionAnswerResponse
from .services import GeminiVocabularyService, QuestionAnswerService


# FastAPI Application
app = FastAPI(title="English Educator API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# simple key word stroage
vocabulary_storage = {}
qa_storage = {}

# Initialize Gemini Service
vocab_service = GeminiVocabularyService()

qa_service = QuestionAnswerService()


@app.get("/")
async def root():
    return {"message": "Welcome to the Vocabulary Extraction API"}


# API Endpoint
@app.post("/extract-vocabulary/", response_model=VocabularyResponse)
async def extract_vocabulary(text: str):
    # Validate input
    if not text or len(text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Input text is too short")

    # Extract vocabulary
    result = await vocab_service.extract_vocabulary(text)

    # Store vocabulary in memory
    key = hash(text)
    vocabulary_storage[key] = VocabularyResponse(**result)

    return vocabulary_storage[key]


@app.post("/extract-question-answer/", response_model=QuestionAnswerResponse)
async def extract_question_answer(text: str):
    # Validate input
    if not text or len(text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Input text is too short")

    # Extract vocabulary
    result = await qa_service.extract_questions_and_answers(text)

    # Store result for retrieval (using hash of text as key for simplicity)
    key = hash(text)
    qa_storage[key] = QuestionAnswerResponse(**result)

    return qa_storage[key]


@app.get("/get-vocabulary/", response_model=Optional[VocabularyResponse])
async def get_vocabulary(text: str):
    """
    Retrieve the vocabulary response for a previously processed text.
    """
    key = hash(text)
    if key in vocabulary_storage:
        return vocabulary_storage[key]
    else:
        raise HTTPException(
            status_code=404, detail="Vocabulary result not found for the provided text"
        )


@app.get("/get-question-answer/", response_model=Optional[QuestionAnswerResponse])
async def get_question_answer(text: str):
    """
    Retrieve the question-answer response for a previously processed text.
    """
    key = hash(text)
    if key in qa_storage:
        return qa_storage[key]
    else:
        raise HTTPException(
            status_code=404,
            detail="Question-answer result not found for the provided text",
        )
