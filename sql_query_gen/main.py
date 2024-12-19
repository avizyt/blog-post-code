import asyncio
import os
import sys
from typing import Union

from dotenv import load_dotenv
import asyncpg

from devtools import debug

from typing_extensions import TypeAlias


from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from models import Deps, Success, InvalidRequest


load_dotenv()

gemini_api_key = os.getenv("GOOGLE_API_KEY")


Response: TypeAlias = Union[Success, InvalidRequest]

model = GeminiModel(
    "gemini-1.5-flash",
    api_key=gemini_api_key,
)

agent = Agent(
    model,
    result_type=Response,  # type: ignore
    deps_type=Deps,
)


async def main():
    if len(sys.argv) == 1:
        prompt = "Please create a SELECT query"
    else:
        prompt = sys.argv[1]

    # connection to database
    conn = await asyncpg.connect(
        user="postgres",
        password="avizyt",
        host="localhost",
        port=5432,
        database="dvdrental",
    )
    try:
        deps = Deps(conn)
        result = await agent.run(prompt, deps=deps)
        result = debug(result.data)
        print("=========Your Query=========")
        print(debug(result.sql_query))
        print("=========Explanation=========")
        print(debug(result.explanation))

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
