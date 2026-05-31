import json

har_path = "/Users/jesusarguelles/Downloads/vertexaisearch.cloud.google.com-streamassist-5.har"

with open(har_path, 'r') as f:
    data = json.load(f)

entry = data['log']['entries'][11]
res_text = entry['response']['content'].get('text', '')

with open("/Users/jesusarguelles/.gemini/antigravity-cli/brain/13795b1e-7bc1-4f33-a601-7e7f419e67b7/scratch/stream_assist_5_dump.txt", "w") as f:
    f.write(res_text)

print("Dumped response text to stream_assist_5_dump.txt")
