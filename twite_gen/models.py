from typing import Optional, List
from pydantic import BaseModel


class ArticleContent(BaseModel):
    title: str
    content: str
    author: Optional[str]
    url: str


class TwitterThread(BaseModel):
    tweets: List[str]
    hashtags: List[str]
