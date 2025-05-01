# ✨ Classification - v1.0 ✨

**(Powered by Gemini 2.5 & Flet)**

Welcome to the large language model classificator.

---

## 🚀 Mission Overview

The Product (`front.py`) provides a streamlined graphical interface to:

1.  **Input** a list of raw product names.
2.  **Query** a local product dataset (`florida_connecticut_product_name_examples.csv`).
3.  **Engage** the Vertex AI Gemini model (`gemini-2.5-flash-preview-04-17`) for intelligent classification of each matched product.
4.  **Display** the input name, the pre-mapped name from the dataset, and the AI-detected label side-by-side, highlighting matches and discrepancies.

This tool is designed for rapid validation and analysis of product labeling consistency using advanced AI.

---

## 🛠️ System Requirements & Pre-flight Checks

Before initiating the App, ensure your system meets the following specifications:

*   **Python:** Version 3.13 or newer. The future requires modern runtimes!
*   **`uv` Package Manager:** We utilize the high-speed `uv` for dependency management. Install it if you haven't already:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Synchronize all the libraries required for this project:

[pyproject.toml here](pyproject.toml)

```bash
uv sync
```

Change the variables inside the [front.py](front.py):

project = "<YOUR_PROJECT>"  
location = "us-central1"  
gen_model = "gemini-2.5-flash-preview-04-17"  

Run it!

```bash
uv run front.py
```

---
## Additional Tools

Look at the [notebook_exp.py](notebook_exp.py) which handles clustering / embeddings and genai.