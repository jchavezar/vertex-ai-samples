with open("generate_2076_readme.py", "r") as f:
    text = f.read()

import re

# We need to insert the missing "INTERFACE TOPOLOGIES" right before the config header.

topologies_content = """<br/>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./public/assets/header_topologies.svg">
    <source media="(prefers-color-scheme: light)" srcset="./public/assets/header_topologies.svg">
    <img alt="Interface Topologies Header" src="./public/assets/header_topologies.svg" width="100%">
  </picture>
</p>

<blockquote>
  <p><b>ARCHITECTURE DUALITY:</b> The Vertex AI Search backend can be consumed via two distinct presentation layers. Choose your methodology.</p>
</blockquote>

<details open>
<summary><kbd>TOPOLOGY A</kbd> <b>Native Gemini Enterprise Interface (Zero-Code)</b></summary>
<br/>
<table>
  <tr>
    <td valign="top">
      <kbd>EXECUTE</kbd> Navigate to <b>GCP Console</b> &gt; <b>Agent Builder</b> &gt; <b>deloitte-demo</b>.<br/><br/>
      <kbd>DEFINE</kbd> Ensure the SharePoint datastore is connected and fully synced.<br/><br/>
      <kbd>OPERATE</kbd> Click <b>Preview</b> to utilize the out-of-the-box Gemini UI.<br/><br/>
      <kbd>RESULT</kbd> Instantly chat, search, and retrieve grounded financial data directly from Microsoft SharePoint without deploying any custom React code.
    </td>
    <td width="400" valign="top">
      <img src="./public/screenshots/native_datastore_status.png" width="400" style="border-radius: 8px;" />
      <br/><br/>
      <img src="./public/screenshots/native_search_results.png" width="400" style="border-radius: 8px;" />
    </td>
  </tr>
</table>
</details>

<br/>

<details open>
<summary><kbd>TOPOLOGY B</kbd> <b>Custom React Neo-Monolith (WIF Required)</b></summary>
<br/>
<table>
  <tr>
    <td valign="top">
      <kbd>EXECUTE</kbd> Utilize this repository's precise brutalist UI.<br/><br/>
      <kbd>DEFINE</kbd> This methodology bypasses the preview interface and calls the Discovery Engine API directly using <b>Workforce Identity Federation (WIF)</b> coupled with Entra ID.<br/><br/>
      <kbd>OPERATE</kbd> Follow the rigorous 6-Phase Pipeline below to orchestrate the auth handshake.
    </td>
    <td width="400" valign="top">
      <img src="./public/screenshots/search_results.png" width="400" style="border-radius: 8px;" />
    </td>
  </tr>
</table>
</details>

<br/>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./public/assets/header_config.svg">
"""

text = text.replace('''<br/>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./public/assets/header_config.svg">''', topologies_content)

# Fix the SVG Cursor overlap (reduce offset to 17 width)
# Because Courier New is ~16.8 on Windows/Mac, but maybe narrower on Linux. Let's make it 21.0 just to be safe, or 21.5, or better:
# Instead of hardcoding width, let's use `textLength` in SVG? SVG doesn't support textLength for cursor positioning natively without JS.
# Let's give it a generous + 10px buffer. 
# 30 + len(title)*16 + (len(title)*4) = 30 + len(title)*20. Let's add +15 to the end.
text = re.sub(r'<rect x="\{30 \+ len\(title\)\*20\.8\}" y="15" width="15"', r'<rect x="{40 + len(title)*20.8}" y="15" width="15"', text)

with open("generate_2076_readme.py", "w") as f:
    f.write(text)

