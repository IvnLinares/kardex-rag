from pydantic import BaseModel, field_validator


class ChatRequest(BaseModel):
    question: str

    @field_validator("question")
    @classmethod
    def question_not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("question no puede estar vacia")
        if len(stripped) > 500:
            raise ValueError("question no puede superar los 500 caracteres")
        return stripped
