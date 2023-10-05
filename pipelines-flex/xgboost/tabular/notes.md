gcloud iam service-accounts add-iam-policy-binding REDACTED_PROJECT_NUMBER-compute@developer.gserviceaccount.com  --member=serviceAccount:REDACTED_PROJECT_NUMBER@cloudbuild.gserviceaccount.com --role=roles/iam.serviceAccountUser --project vtxdemos


Create trigger:

Cloud Console > Cloud Build > Trigger
- Name
- Create and connect to repository -> GitHub