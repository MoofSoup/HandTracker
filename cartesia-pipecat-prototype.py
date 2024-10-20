import os
import asyncio
import logging
from datetime import datetime
from dataclasses import dataclass


from pipecat.frames.frames import (
    Frame,
    TTSAudioRawFrame,
    StartFrame,
    EndFrame
)
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineTask
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.frame_direction import FrameDirection
from pipecat.pipeline.frame_processor import FrameProcessor

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Mock LLM context frame
@dataclass
class MockLLMContextFrame(Frame):
    content: str

# Mock TTS processor
class MockTTSProcessor(FrameProcessor):
    def __init__(self):
        super().__init__()
        self.api_key = os.environ.get('CARTESIA_API_KEY')
        self.voice_id = os.environ.get('CARTESIA_VOICE_ID')
        logger.info(f"Initialized MockTTSProcessor with voice_id: {self.voice_id}")

    async def __call__(self, frame, next_processor):
        logger.debug(f"Processing frame in MockTTSProcessor: {frame}")
        
        # Handle incoming frames
        if frame.direction == FrameDirection.IN:
            if isinstance(frame, MockLLMContextFrame):
                logger.info(f"Generating TTS audio for content: {frame.content}")
                # Simulate processing delay
                await asyncio.sleep(0.1)
                # Generate mock audio data
                audio_data = b'mock_audio_data'
                tts_frame = TTSAudioRawFrame(audio=audio_data, sample_rate=16000, num_channels=1)
                logger.debug(f"Passing TTSAudioRawFrame to next processor")
                await next_processor(tts_frame)
            else:
                await next_processor(frame)
        else:
            # For outgoing frames, simply pass them through
            await next_processor(frame)

# Verification processor
class VerificationProcessor(FrameProcessor):
    def __init__(self):
        super().__init__()

    async def __call__(self, frame, next_processor):
        logger.debug(f"Processing frame in VerificationProcessor: {frame}")
        
        # Handle incoming frames
        if frame.direction == FrameDirection.IN:
            if isinstance(frame, TTSAudioRawFrame):
                logger.info("Verified TTSAudioRawFrame")
                assert frame.audio == b'mock_audio_data', "Unexpected audio data"
                assert frame.sample_rate == 16000, "Unexpected sample rate"
                assert frame.num_channels == 1, "Unexpected number of channels"
        # For outgoing frames or other frames, simply pass them through
        await next_processor(frame)

async def main():
    logger.info("Initializing pipeline")
    
    # Create pipeline
    pipeline = Pipeline([
        MockTTSProcessor(),
        VerificationProcessor()
    ])

    # Create runner and task
    runner = PipelineRunner()
    task = PipelineTask(pipeline)

    # Run the pipeline
    logger.info("Starting pipeline execution")
    start_time = datetime.now()

    await task.queue_frame(StartFrame(clock=None))
    await task.queue_frame(MockLLMContextFrame(content="Hello"))
    await task.queue_frame(EndFrame())

    try:
        await runner.run(task)
    except Exception as e:
        logger.error(f"Error during pipeline execution: {e}")
    else:
        logger.info("Pipeline execution completed successfully")
    
    end_time = datetime.now()
    execution_time = (end_time - start_time).total_seconds()
    logger.info(f"Total execution time: {execution_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())