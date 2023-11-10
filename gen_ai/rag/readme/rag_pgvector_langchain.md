## Create a cloud sql database instance in Google Cloud.

```bash

gcloud sql instances create {instance_name} --database-version=POSTGRES_15 \
    --region={region} --cpu=1 --memory=4GB --root-password={database_password}
```

## Create a table database

```bash
gcloud sql databases create {database_name} --instance={instance_name}

```