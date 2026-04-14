# adk-script-test

A minimal test to verify [Google ADK](https://google.github.io/adk-docs/) works end-to-end — an `LlmAgent` generates a bash script at runtime, saves it, and executes it.

## What it does

1. Creates an ADK `LlmAgent` backed by `gemini-2.5-flash` (via Vertex AI)
2. Asks the agent to write a bash script
3. Saves the output as `generated_script.sh`
4. Executes it

## Setup

```bash
cp .env.example .env
# Edit .env with your project/location if needed
```

## Run

```bash
source .env && uv run python test_adk.py
```

Or inline:

```bash
GOOGLE_GENAI_USE_VERTEXAI=1 GOOGLE_CLOUD_PROJECT=vtxdemos GOOGLE_CLOUD_LOCATION=us-central1 uv run python test_adk.py
```

## Expected output

```
Agent finished generating script. Content:
--------------------------------------------------
#!/bin/bash
echo 'Hello from ADK generated script!'
--------------------------------------------------
Saved into generated_script.sh and made executable.
Executing generated script:
>>>
Hello from ADK generated script!
<<<
```
