import asyncio
from pipecat.processors.frame_processor import FrameProcessor, FrameDirection
from pipecat.frames.frames import (
    Frame,
    LLMMessagesFrame,
    StartFrame,
    EndFrame,
)

class TriggerProcessor(FrameProcessor):
    """A processor that, after a delay, emits an LLM Context frame with 'hello world'."""

    def __init__(self, delay=20):
        super().__init__()
        self.delay = delay
        self.started = False

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        if isinstance(frame, StartFrame) and not self.started:
            self.started = True
            # Start the coroutine to emit the LLM Context frame after a delay
            asyncio.create_task(self.emit_llm_context())

        # Pass all frames downstream
        await self.push_frame(frame, direction)

    async def emit_llm_context(self):
        # Wait for the specified delay
        await asyncio.sleep(self.delay)
        # Create the LLM Context frame with 'hello world'
        llm_frame = LLMMessagesFrame(messages=[{"role": "system", "content": "hello world"}])
        # Emit the frame downstream
        await self.push_frame(llm_frame)