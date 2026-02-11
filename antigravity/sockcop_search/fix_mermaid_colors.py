with open("generate_2076_readme.py", "r") as f:
    text = f.read()

# We need to replace the plain ```mermaid\nsequenceDiagram with the themed version
old_mermaid = """```mermaid
sequenceDiagram"""

# The fresh colors requested by the user (extracted from the second screenshot which looks like standard mermaid base theme with custom variables)
# Light purples, cool blues, soft greens with rounded borders.
new_mermaid = """```mermaid
%%{
  init: {
    'theme': 'base',
    'themeVariables': {
      'primaryColor': '#ede9fe',
      'primaryTextColor': '#0f172a',
      'primaryBorderColor': '#c4b5fd',
      'lineColor': '#94a3b8',
      'secondaryColor': '#f0fdf4',
      'tertiaryColor': '#e0f2fe',
      'actorBkg': '#ede9fe',
      'actorBorder': '#c4b5fd',
      'signalColor': '#475569',
      'signalTextColor': '#475569',
      'noteBkgColor': '#fef08a',
      'noteTextColor': '#0f172a',
      'noteBorderColor': '#fde047'
    }
  }
}%%
sequenceDiagram"""

if old_mermaid in text:
    text = text.replace(old_mermaid, new_mermaid)
    with open("generate_2076_readme.py", "w") as f:
        f.write(text)
    print("Successfully injected custom Mermaid color theme.")
else:
    print("Could not find the Mermaid block to replace.")

