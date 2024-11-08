import asyncio
from sockcop_vertexai import Model

model = Model(
    project="vtxdemos",
    location="us-west1",
    model="gemini-1.5-flash-001"
)

results = asyncio.run(model.generate_content(  # Direct call
    prompt="whats happening in this frame? how many seconds are?",
    yt_link="https://www.youtube.com/watch?v=sydxML4wIKQ",
    video_length_to_process=40 # total seconds
))
print(results)