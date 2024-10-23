import asyncio

from pipecat.frames.frames import EndFrame, TextFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineTask
from pipecat.pipeline.runner import PipelineRunner
from pipecat.services.cartesia import CartesiaTTSService
from pipecat.transports.services.daily import DailyParams, DailyTransport

async def main():
    transport = DailyTransport(
        room_url="https://pc-27c3722f19084f8e8562496f55d034fa.daily.co/testtesttest",
        token="",
        bot_name="hello daily",
        params=DailyParams(audio_out_enabled=True),
    )
    tts = CartesiaTTSService(
        api_key="255b5942-d0a5-4e38-8458-5622d747dcf7",
        voice_id="726d5ae5-055f-4c3d-8355-d9677de68937"
    )

    pipeline = Pipeline(
        [tts, transport.output()]
    )

    task = PipelineTask(pipeline)

    runner = PipelineRunner()

    

    @transport.event_handler("on_first_participant_joined")
    async def on_first_participant_joined(transport, participant):
        participant_name= participant.get("info",{}).get("userName", "")
        await task.queue_frame(TextFrame(f"Hello there, {participant_name}!"))
    @transport.event_handler("on_participant_left")
    async def on_participant_left(transport, participant, reason):
        await task.queue_frame(EndFrame())

    await runner.run(task)
    
if __name__ == "__main__":
    asyncio.run(main())