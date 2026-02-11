
with open("generate_2076_readme.py", "r") as f:
    text = f.read()

# Fix Gradients
old_grad = """    <linearGradient id="grad_{filename}" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.8" />
      <stop offset="100%" stop-color="#0f172a" stop-opacity="0" />
    </linearGradient>"""
    
new_grad = """    <linearGradient id="grad_{filename}" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#1e293b" stop-opacity="1" />
      <stop offset="100%" stop-color="#0f172a" stop-opacity="0" />
    </linearGradient>"""
    
text = text.replace(old_grad, new_grad)


import re
# Fix cursor math
text = re.sub(r'<rect x="\{.*?len\(title\).*?\}" y="15"', '<rect x="{30 + len(title)*20.8}" y="15"', text)

with open("generate_2076_readme.py", "w") as f:
    f.write(text)

