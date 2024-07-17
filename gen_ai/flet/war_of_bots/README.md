# War of Bots ⚔️🤖

This project pits two large language models (LLMs) against each other in a conversational "battle of wits," allowing them to discuss a chosen topic and showcasing their unique approaches to language generation.

![hippo](war_of_bots_1.gif)

## Project Overview

The "War of Bots" aims to:

- **Compare and contrast the conversational styles of different LLMs** (currently, ChatGPT-4 and Google's Gemini Pro).
- **Highlight the strengths and weaknesses of each LLM** in terms of wit, insight, and ability to engage in a thought-provoking discussion.
- **Provide an interactive demonstration** of the capabilities of cutting-edge AI language models.

## Features

- **Head-to-Head Conversation:**  ChatGPT-4 and Gemini Pro take turns responding to a user-defined topic, simulating a back-and-forth dialogue.
- **Response Timing:** The time taken by each LLM to generate its response is displayed, providing insights into their processing speeds.
- **Grounding Verification (Gemini Pro):** Gemini Pro's responses are optionally verified using Google Search and a "grounding" mechanism to assess the accuracy and provide supporting citations.

## Technologies Used

**Frontend:**
- **Flet:** A Python framework for building interactive web UIs, chosen for its ease of use and Python integration.

**Backend:**
- **Python:** The primary programming language for backend logic, API calls, and data handling.
- **OpenAI API:** Used to interact with ChatGPT-4, enabling prompt submission and response retrieval.
- **Google Vertex AI API (Generative Models):** Used to interact with Google's Gemini Pro model, including grounding features.

**Libraries:**
- `openai`: The official OpenAI Python library for API communication. ([https://pypi.org/project/openai/](https://pypi.org/project/openai/))
- `vertexai`: The Google Cloud Vertex AI Python client library. ([https://pypi.org/project/google-cloud-aiplatform/](https://pypi.org/project/google-cloud-aiplatform/))
- `time`: Python's built-in time module for measuring response times.
- `json`: Python's built-in JSON module for handling structured data.
- `base64`:  Potentially used for data encoding/decoding (if applicable to your implementation).

## Installation and Setup

1. **Clone the Repository:**  `git clone https://github.com/your-username/war-of-bots.git`
2. **Navigate to the Project Directory:** `cd war-of-bots`
3. **Create a Virtual Environment (Recommended):** `python3 -m venv .venv`
4. **Activate the Virtual Environment:**
    - Linux/macOS: `source .venv/bin/activate`
    - Windows: `.venv\Scripts\activate`
5. **Install Dependencies:** `pip install -r requirements.txt`

## Configuration

1. **API Keys:**
    - Obtain your OpenAI API key from [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)
    - Set up a Google Cloud project and enable the Vertex AI API. Get your credentials.
2. **Environment Variables:**
    - Create a `.env` file in the project's root directory and store your API keys:
      ```
      OPENAI_API_KEY=your-openai-api-key
      GOOGLE_APPLICATION_CREDENTIALS=path/to/your/google_credentials.json
      ```

## Running the Application

1. **Start the Flet Application:** `flet run main.py` (or the name of your main Flet file).
2. **Access in Browser:** Open your web browser and go to the URL provided by Flet (usually `http://localhost:8550`).

## Usage

1. **Enter a Topic:**  Type a topic or question into the input field on the right.
2. **Start the Conversation:**  Press Enter to initiate the discussion between the LLMs.
3. **Observe the Responses:**  The bots' responses, along with their response times, will be displayed in the left panel.
4. **Grounding (Gemini Pro):**  (Optional) Click the "grounding" button next to Gemini Pro's responses to see the justification, veracity score, and citations.

## Contributing

Contributions are welcome! Feel free to open issues, submit pull requests, or propose new features.

## License

[Choose an appropriate license for your project (e.g., MIT, Apache-2.0)](https://choosealicense.com/) 