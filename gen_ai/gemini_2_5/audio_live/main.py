#%%
import asyncio
import os
from typing import Any, Dict, List, Optional
from IPython.display import Audio, Markdown, display
from google.genai.types import (
    AudioTranscriptionConfig,
    Content,
    LiveConnectConfig,
    Part,
    ProactivityConfig,
    FunctionResponse,
)
import numpy as np
from google import genai

MODEL_ID = "gemini-live-2.5-flash-preview-native-audio-09-2025"
turn_on_the_lights = {"name": "turn_on_the_lights"}
turn_off_the_lights = {"name": "turn_off_the_lights"}

tools = [{"function_declarations": [turn_on_the_lights, turn_off_the_lights]}]

client = genai.Client(
    vertexai=True,
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION")
)

def configure_session(
        system_instruction: Optional[str] = None,
        enable_transcription: bool = True,
        enable_proactivity: bool = False,
        enable_affective_dialog: bool = False,
) -> LiveConnectConfig:
    input_transcription = AudioTranscriptionConfig() if enable_transcription else None
    output_transcription = AudioTranscriptionConfig() if enable_transcription else None
    proactivity = (
        ProactivityConfig(proactive_audio=True) if enable_proactivity else None
    )

    config = LiveConnectConfig(
        response_modalities=["AUDIO"],
        system_instruction=system_instruction,
        input_audio_transcription=input_transcription,
        output_audio_transcription=output_transcription,
        proactivity=proactivity,
        enable_affective_dialog=enable_affective_dialog,
        tools=tools
    )

    return config

session_config = configure_session(
    system_instruction="You are an AI assistant who loves Italian cooking. You can also control the lights using your tools. Your primary language is Italian, but you must respond to commands in the language of the command.",
    enable_proactivity=True,
)

async def send_and_receive_turn(
        session: genai.live.AsyncSession, text_input: str
) -> Dict[str, Any]:
    display(Markdown("\n---"))
    display(Markdown(f"**Input:** {text_input}"))

    await session.send_client_content(
        turns=Content(role="user", parts=[Part(text=text_input)])
    )

    audio_data = []
    input_transcriptions = []
    output_transcriptions = []
    function_call_performed = False

    async for message in session.receive():
        print(message)

        if message.tool_call and not function_call_performed:
            function_responses = []

            for fc_wrapper in message.tool_call.function_calls:
                function_name = fc_wrapper.function_call.name

                function_response = FunctionResponse(
                    id=message.tool_call.tool_call_id,
                    name=function_name,
                    response={
                        "result": f"I confirm. I have executed the action {function_name} successfully. The lights are now ON."
                    }
                )
                function_responses.append(function_response)

            await session.send_tool_response(function_responses=function_responses)

            function_call_performed = True
            continue

        if message.server_content:

            if (
                    message.server_content.input_transcription
                    and message.server_content.input_transcription.text
            ):
                input_transcriptions.append(message.server_content.input_transcription.text)

            if (
                    message.server_content.output_transcription
                    and message.server_content.output_transcription.text
            ):
                output_transcriptions.append(
                    message.server_content.output_transcription.text
                )

            if (
                    message.server_content.model_turn
                    and message.server_content.model_turn.parts
            ):
                for part in message.server_content.model_turn.parts:
                    if part.inline_data:
                        audio_data.append(
                            np.frombuffer(part.inline_data.data, dtype=np.int16)
                        )

    results = {
        "audio_data": audio_data,
        "input_transcription": "".join(input_transcriptions),
        "output_transcription": "".join(output_transcriptions),
    }

    if results["input_transcription"]:
        display(Markdown(f"**Input transcription >** {results['input_transcription']}"))

    if results["audio_data"]:
        full_audio = np.concatenate(results["audio_data"])
        display(
            Audio(full_audio, rate=24000, autoplay=True)
        )
    else:
        display(
            Markdown(
                "**Model Response:** *No audio response received (filtered by system instruction).*"
            )
        )

    if results["output_transcription"]:
        display(
            Markdown(f"**Output transcription >** {results['output_transcription']}")
        )

    return results

async def run_live_session(
        model_id: str,
        config: LiveConnectConfig,
        turns: List[str],
):
    display(Markdown("## Starting Live Connect Session..."))
    system_instruction = config.system_instruction
    display(Markdown(f"**System Instruction:** *{system_instruction}*"))

    try:
        async with client.aio.live.connect(
                model=model_id,
                config=config,
        ) as session:
            display(
                Markdown(f"**Status:** Session established with model: `{model_id}`")
            )

            all_results = []
            for turn in turns:
                result = await send_and_receive_turn(session, turn)
                all_results.append(result)

            display(Markdown("\n---"))
            display(Markdown("**Status:** All turns complete. Session closed."))
            return all_results
    except Exception as e:
        display(Markdown(f"**Error:** Failed to connect or run session: {e}"))
        return []

conversation_turns = [
    "Hey, I was just thinking about my dinner plans. I really love cooking.",
    "Oh yes, me too. I love French cuisine, especially making a good coq au vin. I think I'll make that tonight.",
    "Hmm, that sounds complicated. I prefer Italian food. Say, do you know how to make a simple Margherita pizza recipe?",
    "Turn on the lights please"]

if __name__ == "__main__":
    results = asyncio.run(run_live_session(MODEL_ID, session_config, conversation_turns))