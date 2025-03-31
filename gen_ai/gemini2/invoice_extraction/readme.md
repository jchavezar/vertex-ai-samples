This repository showcases a cutting-edge invoice extraction tool powered by Google's **Gemini 2.0** model. It provides a seamless user experience through a modern **Flet**-based graphical interface, allowing you to effortlessly extract information from invoices and engage in intelligent conversations about the extracted data.

## ✨ Key Features

*   **Intelligent Invoice Parsing**: Utilizes the power of **Gemini 2.0-flash-001** [1] to accurately extract every single value from your invoice documents [1].
*   **Structured Data Output**: The extracted information is returned in a well-defined **JSON schema** [1], ensuring data integrity and easy integration with other systems.
*   **Interactive UI**: A user-friendly interface built with **Flet** [2] allows for easy file uploads and visualization of the extracted data [2].
*   **Conversational AI**: Ask questions about your invoice and receive intelligent answers powered by Gemini's conversational capabilities [1]. The bot leverages the extracted invoice data as context for more relevant responses [1, 3].
*   **Real-time Feedback**: Provides clear feedback during the processing stages, including "Processing invoice..." and "Invoice loaded. Ask me anything!" messages [4].
*   **Error Handling**: Robust error handling is implemented to gracefully manage file processing and API communication issues [1, 3, 4].

## ⚙️ Architecture

The project is structured into two main Python files:

*   **`back.py`**: This file handles the backend logic, interacting directly with the Gemini API [1].
    *   **Initialization**: Sets up the Gemini client, specifying the project (`vtxdemos`), location (`us-central1`), and the **Gemini 2.0-flash-001** model [1].
    *   **System Instruction**: Defines a clear **system instruction** for Gemini, instructing it to act as an OCR expert focused on extracting all values [1].
    *   **Response Schema**: Specifies a detailed **JSON schema** that outlines the expected structure of the extracted invoice data, including fields like `invoice_id`, `payer_name`, `payer_address`, dates, `balance_due`, a `table` of items, subtotals, discounts, tax, total, amount paid, notes, and terms [1].
    *   **`generate_content(file_location: str) -> json`**: This function takes the path to a PDF invoice file [1]. It reads the file content and sends it to the Gemini model along with the "extract" prompt and the defined configuration (including the system instruction and response schema) [1]. The function returns the Gemini's response as a JSON string [1]. Error handling is included to catch potential issues during file reading or API interaction [1].
    *   **`conversational_bot(prompt: str, history: str = None) -> str`**: This function enables conversational interaction. It takes a user `prompt` and an optional `history` (which in this case can be the extracted invoice data) [1]. It sends the prompt to Gemini, configured as an invoice parsing expert [1]. If `history` is provided, it's included in the context to allow the bot to answer questions based on the extracted invoice information [1, 3]. The function maintains a `chat_history` to keep track of the conversation [1]. Error handling is also in place [1].

*   **`front.py`**: This file builds the frontend user interface using the **Flet** library [2].
    *   **Import Statements**: Imports necessary libraries including `json` for handling JSON data, `flet` for the UI, and the backend functions (`generate_content`, `conversational_bot`) from `back.py` [2].
    *   **`build_invoice_view(invoice_data_list)`**: This function takes a list containing the parsed invoice data [2]. It dynamically creates a `ListView` to display the extracted invoice details in a user-friendly format [2]. It iterates through the `invoice_data` and creates `Row`s for key-value pairs and a `DataTable` to display the table of items [2, 5].
    *   **`main(page: Page)`**: This is the main function that sets up the Flet application [5].
        *   **Page Configuration**: Sets the page title, window size, and alignment [5].
        *   **UI Elements**: Creates a `chat_display_area` to show messages, a `gemini` container to display the extracted invoice view, a `chat_container` for the chat interface, a `txt_input_field` for user input, a `send_button`, and an `upload_button` [3, 5, 6].
        *   **`pick_files_result(e: FilePickerResultEvent)`**: This crucial function is triggered after the user selects a PDF file [4]. It displays a `ProgressRing`, calls the `generate_content` function from `back.py` to process the selected file, and upon receiving the JSON response, it parses the data and uses `build_invoice_view` to update the `gemini` container with the extracted information [4]. It also handles potential `JSONDecodeError` and other exceptions, displaying appropriate error messages in the `chat_display_area` [4]. The raw JSON response is temporarily stored in the page session [3, 4].
        *   **`pick_files(e)`**: Opens the `FilePicker` dialog, allowing the user to select a PDF file [3].
        *   **`send_message_click(e)`**: Handles the "Send" button click [3]. It retrieves the user's input, appends it to the `chat_display_area`, and calls the `conversational_bot` function from `back.py` [3]. It passes the user's question and the extracted invoice data (if available in the session) as context to the bot [3]. The bot's response is then displayed in the `chat_display_area` [3]. Error handling for the bot interaction is also included [3].
        *   **Layout**: Arranges the header, body (containing the `gemini` and `chat_container`), and bottom (containing the input field and buttons) in the page [3, 6].
    *   **App Launch**: The `if __name__ == "__main__": app(target=main)` line starts the Flet application [6].

## 🚀 Getting Started

1.  **Prerequisites**: Ensure you have Python installed on your system. You will also need to install the necessary libraries: `flet` and the Google Cloud AI Platform GenAI library.
2.  **API Key**: You will need to set up a Google Cloud project and obtain the necessary credentials to access the Gemini API. **Note**: This repository excerpt does not explicitly detail the authentication process, so refer to the official Google Cloud documentation for setting up API keys or service accounts.
3.  **Installation**:
    ```bash
    pip install flet google-generativeai
    ```
4.  **Running the Application**: Navigate to the repository directory in your terminal and run the `front.py` script:
    ```bash
    python front.py
    ```
    This will open the invoice extraction application in a new window.
5.  **Usage**:
    *   Click the **"Upload PDF Invoice"** button to select an invoice file.
    *   Once the invoice is processed, the extracted information will be displayed in the top section.
    *   You can then type questions about the invoice in the **"Ask something about the invoice..."** field and click **"Send"** to get answers from the AI-powered chat bot.

## 💡 Potential Future Enhancements

*   **Multi-invoice Processing**: Allow users to upload and process multiple invoices simultaneously.
*   **Data Export**: Implement functionality to export the extracted data in various formats (e.g., CSV, Excel).
*   **Configuration Options**: Provide options to customize the extraction schema or model parameters.
*   **Enhanced UI/UX**: Further refine the user interface for improved usability and visual appeal.
*   **More Sophisticated Conversational Features**: Implement more advanced dialogue management and question answering capabilities.

This project offers a glimpse into the future of document processing, combining the power of multimodal AI with intuitive user interfaces to streamline invoice extraction and analysis.