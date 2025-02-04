# Retail Product Search with Gemini and Flet

This project demonstrates a multi-page web application built with Flet, integrating Gemini for product search and conversational AI capabilities.  It leverages vector search for efficient retrieval of relevant products and provides an interactive chat interface for users to ask questions about specific items.

## Table of Contents

* [Features](#features)
* [Installation](#installation)
* [Usage](#usage)
* [Architecture](#architecture)
* [Code Overview](#code-overview)
    * [first_page.py](#first_pagepy)
    * [middleware.py](#middlewarepy)
    * [route.py](#routepy)
    * [search_result.py](#search_resultpy)
    * [second_page.py](#second_pagepy)
* [Dependencies](#dependencies)
* [Future Enhancements](#future-enhancements)
* [Contributing](#contributing)
* [License](#license)

## Features

* **Product Search:**  Users can search for products using a text query. The application uses a hybrid approach combining multimodal (image and text) embeddings for accurate and relevant results.
* **Interactive Chat:**  On the product details page, users can interact with a conversational AI ("Chatsy") powered by Gemini.  They can ask questions about the product and receive helpful responses, including suggested related questions.
* **Multi-Page Navigation:** The application features smooth navigation between different pages, including the search results page and a secondary information page.
* **Visual Product Display:** Search results are displayed in a grid view with product images and basic information.
* **Detailed Product Information:**  The search results page provides detailed information about the selected product, including descriptions, materials, and price.
* **Dynamic Question Suggestions:** Chatsy suggests relevant questions to the user, categorized for clarity and prompting further interaction.
* **Cached Search Results:** Improves user experience by caching and displaying previously searched results.

## Installation

1. **Clone the repository:**

```bash
git clone https://github.com/jchavezar/vertex-ai-samples.git
cd tech_immersion/retail_v1.0
```

2. **Install Dependencies:**

```bash
pip install -r requirements.txt  # Create a requirements.txt file with necessary packages.
```

3. **Set up Google Cloud Project:**
   * Ensure you have a Google Cloud Project with Vertex AI enabled.
   * Set the project_id and region variables in middleware.py to your project details.
   * Create a service account with necessary permissions and set the GOOGLE_APPLICATION_CREDENTIALS environment variable.
   * Ensure your dataset is in the specified dataset_uri in middleware.py and the structure matches what the code expects.

4. **Run the app:**

```bash
python route.py
```

# Usage
1. Open the application in your web browser.
2. Use the search bar on the first page to search for products.
3. Click on a product to view its details and interact with Chatsy.
4. Use the buttons at the bottom to navigate between pages.

# Architecture
The application follows a multi-page architecture using Flet. It interacts with Google Cloud's Vertex AI platform for vector search and Gemini for conversational AI.  The middleware.py file handles the interaction with the Vertex AI services.

# Code Overview
<a id="first_pagepy"></a>  # `first_page.py`

This file defines the main page of the application, including the search functionality, product display, and navigation. It uses the middleware.py functions to perform the search and retrieve product data. It also handles the initial display of cached search results.

<a id="middlewarepy"></a>  # `middleware.py`


This file contains the core logic for interacting with Vertex AI.  It includes functions for:

Calculating multimodal embeddings (image and text).
Performing vector search against the product dataset.
Retrieving a list of all items.
Interacting with the Gemini model for chat responses and question generation.

<a id="routepy"></a>  # `route.py`

This file handles the routing between different pages of the Flet application. It defines the main function that sets up the application and manages page navigation.

<a id="search_resultpy"></a>  # `search_result.py`

This file displays the details of a selected product and provides the interactive chat interface. It uses the middleware.py functions to get chat responses from Gemini.

<a id="second_pagepy"></a>  # `second_page.py`

This file contains a secondary page, currently displaying an image. It serves as an example of multi-page navigation in Flet.

# Dependencies
The project uses the following Python packages:

- flet
- pandas
- numpy
- google-cloud-aiplatform
- google-generativeai

You'll need to install these using pip: 

<mark>pip install flet pandas numpy google-cloud-aiplatform google-generativeai</mark>

# Future Enhancements
- Implement user authentication.
- Add more advanced search filters (e.g., by price range, material).
- Improve the chat interface with features like message history and user avatars.
- Implement proper error handling and user feedback.
- Deploy the application to a production environment.

# Contributing
Contributions are welcome! Please open an issue or submit a pull request.

# License
[Choose a license, e.g., MIT]