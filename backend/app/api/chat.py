import json
from collections.abc import AsyncIterator
from dataclasses import asdict

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.models.chat import ChatRequest
from app.rag.chain import Source, astream_answer

router = APIRouter()


async def _sse_stream(question: str) -> AsyncIterator[str]:
    async for chunk in astream_answer(question):
        if isinstance(chunk, list):
            sources = [asdict(s) for s in chunk if isinstance(s, Source)]
            yield f"event: sources\ndata: {json.dumps({'sources': sources})}\n\n"
        elif chunk:
            yield f"data: {json.dumps({'content': chunk})}\n\n"
    yield "event: done\ndata: {}\n\n"


@router.post("/chat")
async def chat(request: ChatRequest) -> StreamingResponse:
    return StreamingResponse(
        _sse_stream(request.question),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
