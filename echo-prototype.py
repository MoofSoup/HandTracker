import asyncio

from pipecat.transports.services.daily import DailyTransport, DailyParams
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.pipeline.task import PipelineTask, PipelineParams
from pipecat.frames.frames import TTSAudioRawFrame
from pipecat.pipeline.pipeline import Pipeline
transport = DailyTransport(
    room_url="",
    token="",
    bot_name="Calli",
    params= DailyParams(audio_out_enabled=True)
)
# next we are going to define some event handlers with python decorators. 

async def main():
    transport= DailyTransport(
        room_url="",
        token="",
        bot_name="Calli",
        params= DailyParams(audio_out_enabled=True)
    )
    pipeline= Pipeline(
        [
            transport.input(),
            tts,
            ta,
            transport.output(),   
        ]
    )
    task= PipelineTask(pipeline, PipelineParams())
    @transport.add_event_handler("on_transcription_message")
    async def on_transcription_message(message):
        text= message.get("text", "")
        if text:
            await task.queue_frame(TTSAudioRawFrame(text=text))
    @transport.add_event_handler("on_first_participant_joined")
    async def on_first_participant_joined(transport, participant):
        transport.capture_participant_transcription(participant["id"])
    