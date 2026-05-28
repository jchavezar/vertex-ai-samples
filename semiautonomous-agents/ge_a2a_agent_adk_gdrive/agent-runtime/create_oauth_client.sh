#!/usr/bin/env bash
#
# OAuth2 client provisioning for the GE Authorization resource (AE variant).
# Identical to the Cloud Run variant — both register the same OAuth2 client
# kind. You can reuse the same client across variants if you prefer.

set -euo pipefail

PROJECT="${PROJECT_ID:-vtxdemos}"

cat <<EOF
============================================================================
Create the OAuth2 web client (one-time, manual)
============================================================================

1.  Open: https://console.cloud.google.com/apis/credentials?project=${PROJECT}

2.  Click  +CREATE CREDENTIALS  ->  OAuth client ID

3.  Application type:   Web application
    Name:               ge-a2a-auth-ae

4.  Authorized redirect URIs — add THESE TWO:

      https://vertexaisearch.cloud.google.com/oauth-redirect
      https://discoveryengine.googleapis.com/v1alpha/authorizations/oauthredirect

5.  Click CREATE, copy Client ID / Client secret into .env:

      OAUTH_CLIENT_ID=...
      OAUTH_CLIENT_SECRET=...

6.  Make sure the OAuth consent screen is published / Internal and
    includes both scopes:

      https://www.googleapis.com/auth/cloud-platform
      https://www.googleapis.com/auth/drive.readonly

7.  Then run:  python create_authorization.py
============================================================================
EOF
