# Building and Deploying a Camera Marketplace App with Generative AI

This project demonstrates a camera marketplace app powered by generative AI. The app allows users to search for cameras by text or video query, leveraging image and text embeddings for semantic search. The backend is built with FastAPI and ScaNN, while the frontend is a Flutter application.

**Key Features**

*   **Generative AI Integration:** Uses the Gemini Pro model for text generation and summarization.
*   **Multimodal Search:** Supports camera searches through both text descriptions and video input.
*   **Scalable Backend:** Deployed on Google Cloud Run for efficient handling of user requests.
*   **Intuitive Flutter Frontend:** Provides a user-friendly interface for browsing and searching cameras.

**Project Structure**

*   **`preprocess.ipynb`:** Creates embeddings for images and text data (essential preprocessing step).
*   **`middleware/`**
    *   **`main.py`:** Backend code using FastAPI, ScaNN, and Uvicorn.
    *   **`requirements.txt`:** Lists Python dependencies for the backend.
    *   **`Dockerfile`:** Defines the container environment for the backend.
*   **`lib/`:** Contains the core Flutter code for the frontend.
    *   **`main.dart`:** Entry point of the Flutter app.
    *   **`next_page.dart`:** UI for displaying camera details.
*   **`pubspec.yaml`:** Lists Flutter dependencies for the frontend.
*   `Dockerfile` (root): Defines the container environment for the frontend.

### Step-by-Step Guide

1.  **Preprocess Data**
    *   Execute `preprocess.ipynb` to generate embeddings from your image and text data. These embeddings will be used for similarity search in the backend.
2.  **Build and Deploy the Backend (Middleware)**

    *   **Local Development:**
        ```bash
        cd middleware
        pip install -r requirements.txt
        uvicorn main:app 
        ```
    *   **Docker:**
        ```bash
        cd middleware
        docker build -t marketplace-backend .
        docker run -p 8080:8080 marketplace-backend
        ```
    *   **Google Cloud Run:**
        ```bash
        gcloud builds submit --tag gcr.io/[YOUR_PROJECT_ID]/marketplace-backend
        gcloud run deploy marketplace-backend --image gcr.io/[YOUR_PROJECT_ID]/marketplace-backend --platform managed
        ```

3.  **Build and Deploy the Frontend**

    *   **Local Development:**
        ```bash
        cd .. (project root)
        flutter pub get
        flutter run -d chrome
        ```
    *   **Docker:**
        ```bash
        # set environment variables
        API_KEY=your_api_key
        docker build --build-arg API_KEY=$API_KEY -t marketplace-frontend .
        docker run -p 80:80 marketplace-frontend
        ```
    *   **Google Cloud Run:**
        ```bash
        gcloud builds submit --tag gcr.io/[YOUR_PROJECT_ID]/marketplace-frontend
        gcloud run deploy marketplace-frontend --image gcr.io/[YOUR_PROJECT_ID]/marketplace-frontend --platform managed --set-env-vars API_KEY=your_api_key 
        ```
    *   **Replace 'YOUR\_API\_KEY' in the frontend `Dockerfile` and the cloud run command** with your valid API key.

## Code Snippets

# Camera Marketplace Frontend - Flutter App

This repository houses the Flutter frontend for the Camera Marketplace application. The app provides a user-friendly interface for browsing and searching cameras, leveraging a backend powered by generative AI.

## Key Features

- **Intuitive Design:** Browse and discover cameras with ease.
- **Multimodal Search:** Search by text descriptions or video input.
- **Generative AI Summaries:** Get concise summaries of camera listings powered by Gemini Pro.
- **Detailed Camera Views:** Explore detailed specifications and information.

## Prerequisites

- **Flutter SDK:** Ensure you have Flutter installed and configured on your system. ([Install Flutter](https://docs.flutter.dev/get-started/install))
- **Google Cloud Project:** You'll need a Google Cloud Project to build and deploy your app.
- **Artifact Registry:** Enable Artifact Registry to store your Docker image.
- **Cloud Run:** Enable Cloud Run to deploy your containerized application.
- **API Key:** Obtain a valid API key for the Gemini Pro model from Google Cloud.

## Building and Deploying

1. **Set API Key (Environment Variable)**
    - Create a file named `.env` in your project's root directory.
    - Add the following line, replacing `YOUR_API_KEY` with your actual API key:
      ```
      API_KEY=YOUR_API_KEY
      ```
    - For additional security, do NOT commit this `.env` file to source control (add it to your `.gitignore`).

2. **Build the Docker Image**
    - Open your terminal and navigate to the project root directory.
    - Run the following command, replacing `[PROJECT-ID]` with your Google Cloud Project ID and `[IMAGE-NAME]` with your desired image name in Artifact Registry:
      ```bash
      gcloud builds submit --tag us-central1-docker.pkg.dev/[PROJECT-ID]/[REPOSITORY]/[IMAGE-NAME] . 
      ```

3. **Deploy to Cloud Run**
    - In your terminal, run the following command, again replacing `[PROJECT-ID]` and `[IMAGE-NAME]`:
      ```bash
      gcloud run deploy [SERVICE-NAME] --image us-central1-docker.pkg.dev/[PROJECT-ID]/[REPOSITORY]/[IMAGE-NAME] --platform managed --region us-central1 --set-env-vars API_KEY=$API_KEY 
      ```
    - Replace `[SERVICE-NAME]` with your preferred Cloud Run service name.
    - This command deploys your containerized Flutter app to Cloud Run, automatically using the `API_KEY` environment variable you set in step 1.
    -  The API_KEY will be accessed in the Dockerfile automatically.


## Local Development
To develop it locally in your machine you can just do:
```bash
flutter pub get
flutter run

