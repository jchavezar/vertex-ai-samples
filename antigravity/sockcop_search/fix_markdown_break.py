with open("generate_2076_readme.py", "r") as f:
    text = f.read()

broken_block = """<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./public/assets/header_config.svg">

    <source media="(prefers-color-scheme: light)" srcset="./public/assets/header_config.svg">
    <img alt="Configuration Pipeline Header" src="./public/assets/header_config.svg" width="100%">
  </picture>
</p>"""

fixed_block = """<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./public/assets/header_config.svg">
    <source media="(prefers-color-scheme: light)" srcset="./public/assets/header_config.svg">
    <img alt="Configuration Pipeline Header" src="./public/assets/header_config.svg" width="100%">
  </picture>
</p>"""

text = text.replace(broken_block, fixed_block)

with open("generate_2076_readme.py", "w") as f:
    f.write(text)

