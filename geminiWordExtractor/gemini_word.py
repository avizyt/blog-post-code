import asyncio
import os
from dotenv import load_dotenv
import google.generativeai as genai


load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")
# print(google_api_key)
# configure Gemini API
genai.configure(api_key=google_api_key)

# Create the model
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

chat_session = model.start_chat(
    history=[
        {
            "role": "user",
            "parts": [
                "Mrs. Bennet, however, with the assistance of her five daughters, could ask on the subject, was sufficient to draw from her husband any satisfactory description of Mr. Bingley. They attacked him in various ways, with barefaced questions, ",
            ],
        },
        {
            "role": "model",
            "parts": [
                '```json\n{\n  "difficult_words": [\n    {\n      "word": "elude",\n      "synonyms": ["evade", "avoid", "escape", "dodge"],\n      "antonyms": ["confront", "face", "encounter"],\n      "usecase": "To cleverly avoid something or someone.",\n      "example": "The thief managed to elude the police."\n    },```',
            ],
        },
    ]
)

input_text = """Mrs. Bennet, however, with the assistance of her five daughters, could ask on the subject, was sufficient to draw from her husband any satisfactory description of Mr. Bingley. They attacked him in various ways, with barefaced questions, ingenious suppositions, and distant surmises; but he eluded the skill of them all; and they were at last obliged to accept the second-hand intelligence of their neighbour, Lady Lucas. Her report was highly favourable. Sir William had been delighted with him. He was quite young, wonderfully handsome, extremely agreeable, and, to crown the whole, he meant to be at the next assembly with a large party. Nothing could be more delightful! To be fond of dancing was a certain step towards falling in love; and very lively hopes of Mr. Bingley’s heart were entertained."""


# response = await chat_session.send_message_async(input_text)
async def process_input_text(text):
    input_text = text
    response = await chat_session.send_message_async(input_text)
    print(response)


# Call the asynchronous function
response = asyncio.run(process_input_text(input_text))
print(response)
