gcloud iam service-accounts add-iam-policy-binding 254356041555-compute@developer.gserviceaccount.com  --member=serviceAccount:254356041555@cloudbuild.gserviceaccount.com --role=roles/iam.serviceAccountUser --project vtxdemos


Create trigger:

Cloud Console > Cloud Build > Trigger
- Name
- Create and connect to repository -> GitHub