import re

with open("video_tools.py", "r") as f:
    tools_code = f.read()

with open("agent.py", "r") as f:
    agent_code = f.read()

# Remove the import of video_tools from agent_code
agent_code = re.sub(r'from video_tools import \([^)]+\)', '', agent_code, flags=re.MULTILINE | re.DOTALL)
agent_code = re.sub(r'from video_tools import .*', '', agent_code)

combined_code = tools_code + "\n\n" + agent_code

with open("agent.py", "w") as f:
    f.write(combined_code)

print("Merged video_tools.py into agent.py")
