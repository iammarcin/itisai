from typing import Any, Optional, Awaitable, Callable, Iterator, Union
from langchain.callbacks.base import AsyncCallbackHandler
from fastapi.responses import StreamingResponse
from starlette.types import Send

Sender = Callable[[Union[str, bytes]], Awaitable[None]]
import logconfig, traceback
logger = logconfig.logger

class EmptyIterator(Iterator[Union[str, bytes]]):
    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration

class AsyncStreamCallbackHandler(AsyncCallbackHandler):
    def __init__(self, send: Sender):
        super().__init__()
        self.send = send

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        await self.send(token)
class ChatStreamingResponse(StreamingResponse):
    def __init__(
            self,
            generate: Callable[[Sender], Awaitable[None]],
            status_code: int = 200,
            media_type: Optional[str] = None,
    ) -> None:
        super().__init__(content=EmptyIterator(), status_code=status_code, media_type=media_type)
        self.generate = generate

    async def stream_response(self, send: Send) -> None:
        await send(
            {
                "type": "http.response.start",
                "status": self.status_code,
                "headers": self.raw_headers,
            }
        )

        async def send_chunk(chunk: Union[str, bytes]):
            if not isinstance(chunk, bytes):
                chunk = chunk.encode(self.charset)
            await send({"type": "http.response.body", "body": chunk, "more_body": True})

        try:
          data = await self.generate(send_chunk)
        except Exception as e:
          logger.error("Error while streaming response: %s" % e)
          traceback.print_exc()
          await send_chunk("Error!!! %s" % e)

        await send({"type": "http.response.body", "body": b"", "more_body": False})
