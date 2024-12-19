import os
from typing import Union


from dotenv import load_dotenv
import asyncpg


from typing_extensions import TypeAlias


from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.models.gemini import GeminiModel

from schema import DB_SCHEMA

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


@agent.system_prompt
async def system_prompt() -> str:
    return f"""\

Given the following PostgreSQL table of records, your job is to
write a SQL query that suits the user's request.

Database schema:
{DB_SCHEMA}

Example
    request:  Find all films with a rental rate greater than $4.00 and a rating of 'PG'
    response: SELECT title, rental_rate
    FROM film
    WHERE rental_rate > 4.00 AND rating = 'PG';
Example
    request: Find the film(s) with the longest length
    response: SELECT title, length
    FROM film
    WHERE length = (SELECT MAX(length) FROM film);
Example
    request: Find the average rental duration for films in each category
    response: SELECT c.name, AVG(f.rental_duration) AS average_rental_duration
    FROM category c
    JOIN film_category fc ON c.category_id = fc.category_id
    JOIN film f ON fc.film_id = f.film_id
    GROUP BY c.name
    ORDER BY average_rental_duration DESC;
"""


@agent.result_validator
async def validate_result(ctx: RunContext[Deps], result: Response) -> Response:
    if isinstance(result, InvalidRequest):
        return result

    # gemini often adds extraneos backlashes to SQL
    result.sql_query = result.sql_query.replace("\\", " ")
    if not result.sql_query.upper().startswith("SELECT"):
        raise ModelRetry("Please create a SELECT query")

    try:
        await ctx.deps.conn.execute(f"EXPLAIN {result.sql_query}")
    except asyncpg.exceptions.PostgresError as e:
        raise ModelRetry(f"Invalid SQL: {e}") from e
    else:
        return result
