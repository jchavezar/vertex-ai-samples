import re

with open("generate_2076_readme.py", "r") as f:
    text = f.read()

# Using a robust regex to find and replace the entire mermaid block with the new IMG tag
pattern = re.compile(r"```mermaid.*?```", re.DOTALL)

# New static image block centered with break tags
new_img_block = """<br/>
<p align="center">
  <img src="./public/assets/auth_topology.svg" alt="Detailed Entra ID / WIF Authorization Sequence" width="100%">
</p>
<br/>"""

text = pattern.sub(new_img_block, text)

with open("generate_2076_readme.py", "w") as f:
    f.write(text)
