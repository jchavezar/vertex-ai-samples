#!/usr/bin/env bash
#
# OAuth2 client provisioning for the GE Authorization resource.
#
# gcloud cannot create web-OAuth-client credentials from the CLI (only SA
# keys and IAP clients). The web client is created manually in the Cloud
# Console; the rest of the pipeline is fully automated.

set -euo pipefail

PROJECT="${PROJECT_ID:-vtxdemos}"

cat <<EOF
============================================================================
Create the OAuth2 web client (one-time, manual)
============================================================================

1.  Open: https://console.cloud.google.com/apis/credentials?project=${PROJECT}

2.  Click  +CREATE CREDENTIALS  ->  OAuth client ID

3.  Application type:   Web application
    Name:               ge-a2a-auth

4.  Authorized redirect URIs — add THESE TWO:

      https://vertexaisearch.cloud.google.com/oauth-redirect
      https://discoveryengine.googleapis.com/v1alpha/authorizations/oauthredirect

    (GE uses both depending on the engine; safe to add both.)

5.  Click CREATE, then copy the Client ID and Client secret into .env:

      OAUTH_CLIENT_ID=...
      OAUTH_CLIENT_SECRET=...

6.  Make sure the OAuth consent screen (Branding) is published / Internal
    and includes the scopes:

      https://www.googleapis.com/auth/cloud-platform
      https://www.googleapis.com/auth/drive.readonly

7.  Then run:  python create_authorization.py
============================================================================
EOF
