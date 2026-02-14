import re
with open("test_deploy.py", "r") as f:
    code = f.read()

new_code = code.replace('"google-cloud-aiplatform[adk,agent_engines]",', '"google-cloud-aiplatform[adk,agent_engines]==1.104.0",')
new_code = new_code.replace('"google-adk",', '"google-adk==1.7.0",')
new_code = new_code.replace('"google-genai",', '"google-genai==1.26.0",')

with open("test_deploy.py", "w") as f:
    f.write(new_code)
