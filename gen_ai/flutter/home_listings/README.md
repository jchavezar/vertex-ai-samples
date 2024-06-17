# Home Listings

This Flutter application showcases a powerful semantic search experience using multimodal embeddings. It leverages Google Vector Search, a robust vector database, to store and retrieve text and image embeddings, enabling users to find relevant information based on meaning rather than just keywords. The front-end is built with Flutter, providing a smooth and intuitive user interface for searching and exploring the data. This project demonstrates the potential of combining cutting-edge technologies like multimodal embeddings and vector databases to create innovative search solutions.
## Getting Started

This project is a starting point for a Flutter application.

A few resources to get you started if this is your first Flutter project:

- [Lab: Write your first Flutter app](https://docs.flutter.dev/get-started/codelab)
- [Cookbook: Useful Flutter samples](https://docs.flutter.dev/cookbook)

For help getting started with Flutter development, view the
[online documentation](https://docs.flutter.dev/), which offers tutorials,
samples, guidance on mobile development, and a full API reference.

## Step 1

After cloning this repo build the middleware in your Google Cloud Project.

*Change the region, project and **artifact registry repo**: {your_region}-docker.pkg.dev/{your_project}/{your-artifact-repository}/house_listings:middleware*
```bash
cd middleware
gcloud builds submit -t us-central1-docker.pkg.dev/vtxdemos/cloud-run-source-deploy/house_listings:middleware .
```

### Deploy to Cloud Run

*Change your variables as before...*
```bash
gcloud run deploy home-listings-middleware --image us-central1-docker.pkg.dev/vtxdemos/cloud-run-source-deploy/house_listings:middleware --region us-central1 --quiet --allow-unauthenticated
```
## Step 2

Build the front end and deploy to Cloud Run.

*Change the region, project and **artifact registry repo**: {your_region}-docker.pkg.dev/{your_project}/{your-artifact-repository}/house_listings:middleware*

```bash
cd ..
gcloud builds submit -t us-central1-docker.pkg.dev/vtxdemos/cloud-run-source-deploy/house_listings:frontend .
```
*Change your variables as before...*
```bash
gcloud run deploy home-listings-frontend --image us-central1-docker.pkg.dev/vtxdemos/cloud-run-source-deploy/house_frontend:middleware --region us-central1 --quiet --allow-unauthenticated
```