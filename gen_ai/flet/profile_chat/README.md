## Getting Started with a Flet-powered Chatbot using Gemini

This repository contains a simple chat application powered by Google Vertex AI's Gemini and Flet.

![hippo](chatbot_profile.gif)
![hippo](chat_profile_2.gif)

### Prerequisites

Before running the application, make sure you have the following:

* **Python 3.7 or later**
* **A Google Cloud Platform project** with billing enabled and the Vertex AI API enabled.
* **A Gemini model deployed**: You can find instructions on how to deploy a Gemini model [here](https://cloud.google.com/vertex-ai/docs/generative-ai/models/test-models).
* **Google Cloud Storage Bucket**: Create a bucket to store your dataset.
* **Service Account**: Create a service account with appropriate permissions (Vertex AI User, Storage Object Admin) to access your resources.
* **Authentication**: Download the JSON key file for your service account and set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable.

### Installation

1. **Clone this repository**:

   ```bash
   git clone https://github.com/jchavezar/vertex-ai-samples.git
   cd vertex-ai-samples/gen_ai/flet/profile_chat
   ```

2. **Install the required Python packages**:

   ```bash
   pip install -r requirements.txt
   ```
   
### Preprocessing

During the following step we will create synthetic data using Gemini and then story in google cloud storage.

Open [profile_search_preprocess](./profile_search_preprocess.ipynb) file and follow the steps.

> Remember to use the same bucket and bucket folder.

### Configuration

1. **Update `backend.py`**:
    * **Project ID:** Replace `"vtxdemos"` with your Google Cloud project ID.
    * **Model ID:**  Replace `"gemini-1.5-flash-001"` with the ID of your deployed Gemini model.
    * **Bucket ID:** Replace `"vtxdemos-vsearch-datasets"` with the name of your Google Cloud Storage bucket.
    * **Blob ID:** Replace `"bucket_folder"` with the path to your bucket folder.

2. **Prepare your Dataset:**
    * Structure your dataset as a JSON file containing profile information. Each profile should be a separate entry in a list with a `description` key containing the profile text.
    * Upload the JSON file to your Google Cloud Storage bucket.

### Running the Application

1. **Start the Flet application:**

   ```bash
   flet run front_end.py
   ```

2. **Access the application:**
    * Open your web browser and navigate to the address displayed in the terminal after running the previous command.

### Using the Chatbot

1.  **Type your message in the input field** at the bottom of the application window.
2.  **Press Enter to send the message**.
3.  **The chatbot will respond** with a generated message based on the context provided in `backend.py` and your input.

### Additional Notes

* **Context Management:** The current implementation provides a basic example of context management. You can enhance it by storing and retrieving previous conversation turns, user profiles, and other relevant information.
* **Grounding:** The code includes commented-out sections related to grounding (justification, veracity, citations). You can uncomment and integrate these features to provide more transparent and reliable responses from the chatbot.
* **Error Handling:** Implement robust error handling mechanisms in your code to handle network issues, invalid inputs, and other potential errors.
* **Security:** Always follow security best practices when developing applications that handle sensitive data. Ensure your Google Cloud Platform resources are properly secured.

### Contributing

Contributions are welcome! If you have any suggestions, bug reports, or feature requests, please open an issue or submit a pull request. 
