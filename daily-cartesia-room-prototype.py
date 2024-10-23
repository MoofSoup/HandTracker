import asyncio
import pipecat
import time

from pipecat.frames.frames import EndFrame, TextFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineTask
from pipecat.pipeline.runner import PipelineRunner
from pipecat.services.cartesia import CartesiaTTSService
from pipecat.transports.services.daily import DailyParams, DailyTransport

async def main():
  # Use Daily as a real-time media transport (WebRTC)
  transport = DailyTransport(
    room_url="https://pc-27c3722f19084f8e8562496f55d034fa.daily.co/testtesttest",
    token="",
    bot_name="Facillitator Agent",
    params=DailyParams(audio_out_enabled=True))

  # Use Cartesia for Text-to-Speech
  tts = CartesiaTTSService(
    api_key="255b5942-d0a5-4e38-8458-5622d747dcf7",
    voice_id="726d5ae5-055f-4c3d-8355-d9677de68937"
  )

  # Simple pipeline that will process text to speech and output the result
  pipeline = Pipeline([tts, transport.output()])

  # Create Pipecat processor that can run one or more pipelines tasks
  runner = PipelineRunner()

  # Assign the task callable to run the pipeline
  task = PipelineTask(pipeline)

  # Register an event handler to play audio when a
  # participant joins the transport WebRTC session
  @transport.event_handler("on_first_participant_joined")
  async def on_first_participant_joined(transport, participant):
    participant_name = participant.get("info", {}).get("userName", "")
    # Queue a TextFrame that will get spoken by the TTS service (Cartesia)
    time.sleep(20)
    await task.queue_frame(TextFrame(f"{participant_name} has had their hand raised for fifteen seconds, and no one has said anything!"))

  # Register an event handler to exit the application when the user leaves.
  @transport.event_handler("on_participant_left")
  async def on_participant_left(transport, participant, reason):
    await task.queue_frame(EndFrame())

  # Run the pipeline task
  await runner.run(task)

if __name__ == "__main__":
  asyncio.run(main())