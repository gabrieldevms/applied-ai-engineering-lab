from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    text: str = Field(
        min_length=1,
        description="Text to be analyzed.",
    )
    language: str = Field(
        default="en",
        min_length=2,
        max_length=10,
        description="Expected language for the analysis response.",
    )


class AnalyzeResponse(BaseModel):
    original_text: str
    summary: str
    word_count: int
    character_count: int
    language: str
