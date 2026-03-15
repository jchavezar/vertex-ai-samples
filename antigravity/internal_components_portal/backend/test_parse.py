import re
import json

with open('/tmp/ge_raw_stream.log', 'r') as f:
    content = f.read()

# Remove the "JSON ERROR: ..." lines that I injected for debugging
content = re.sub(r'JSON ERROR:.*?\n', '', content)

chunks = content.strip()
print(f"Chunks starts with: {chunks[:20]}")

# Since it outputs a list `[{...}, {...}]`, we can just parse it as an array if it's well-formed, 
# or we can extract the objects if it's streamed.

try:
    data = json.loads(chunks)
    print(f"Successfully parsed as JSON array with {len(data)} items")
    for item in data:
         answer_obj = item.get("answer", {})
         print(f"Text snippet: {answer_obj.get('answerText', '')}")
except json.JSONDecodeError as e:
    print(f"Could not parse entirely: {e}")
