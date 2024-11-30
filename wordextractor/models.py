from pydantic import BaseModel, Field
from typing import List, Optional


class WordDetails(BaseModel):
    word: str = Field(..., description="Extracted vocabulary word")
    synonyms: List[str] = Field(
        default_factory=list, description="Synonyms of the word"
    )
    antonyms: List[str] = Field(
        default_factory=list, description="Antonyms of the word"
    )
    usecase: Optional[str] = Field(None, description="Use case of the word")
    example: Optional[str] = Field(None, description="Example sentence")


class VocabularyResponse(BaseModel):
    difficult_words: List[WordDetails] = Field(
        ..., description="List of difficult vocabulary words"
    )
    medium_words: List[WordDetails] = Field(
        ..., description="List of medium vocabulary words"
    )


class QuestionAnswerModel(BaseModel):
    question: str = Field(..., description="Question")
    answer: str = Field(..., description="Answer")


class QuestionAnswerResponse(BaseModel):
    questions_and_answers: List[QuestionAnswerModel] = Field(
        ..., description="List of questions and answers"
    )
