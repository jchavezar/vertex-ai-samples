import time
import asyncio
from sockcop_vertexai import Model

model = Model(
    project="vtxdemos",
    location="us-west1",
    model="gemini-1.5-flash-002"
)

start_time = time.time()
results = asyncio.run(model.generate_content(  # Direct call
    prompt="Give me a description of the following clip",
    yt_link="https://www.youtube.com/watch?v=sydxML4wIKQ",
    video_length_to_process=40
))
print(results)
print(time.time() - start_time)