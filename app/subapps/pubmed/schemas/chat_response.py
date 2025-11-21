from pydantic import BaseModel

class QueryRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str
    references: list