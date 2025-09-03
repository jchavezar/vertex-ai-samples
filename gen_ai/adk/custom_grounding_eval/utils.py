import json
import time
import requests
import google.auth

SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

class Grounding:
    def __init__(self, refresh_token: str, token_url: str, endpoint_url: str):
        self.refresh_token = refresh_token
        self.token_url = token_url
        self.endpoint_url = endpoint_url

    def get_access_token(self):
        """Gets an access token using the refresh token."""
        try:
            response = requests.get(f"{self.token_url}?refresh_token={self.refresh_token}", headers={"Content-Type": "application/json"})
            response.raise_for_status()
            return response.json()["access_token"]
        except requests.exceptions.RequestException as e:
            print(f"Error getting Kensho access token: {e}")
            return f"Error: {e}"

    def get_gcp_access_token(self):
        """Gets a GCP access token using Google's auth library."""
        try:
            credentials, project = google.auth.default(scopes=SCOPES)
            auth_req = google.auth.transport.requests.Request()
            credentials.refresh(auth_req)
            return credentials.token
        except Exception as e:
            print(f"Error getting GCP access token: {e}")
            raise print(f"Failed to retrieve GCP access token {e}")

    def direct_api_call(self, query: str):
        """
        This is a tool that gets information from an endpoint directly

        Arguments:
            - query: The prompt or query to get information from grounding data.
        """
        token = self.get_access_token()

        data = {
            "query":  query
        }
        headers = {
            "Authorization": f"Bearer {token}",
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        retries = 3

        for i in range(retries):
            try:
                response = requests.post(self.endpoint_url, headers=headers, data=json.dumps(data))
                response.raise_for_status()
                return str(response.json())
            except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")
                print(query)
                if i < retries - 1:
                    time.sleep(2) # wait for 2 seconds before retrying
                    print("Retrying...")
                else:
                    return f"Error in grounding tool: {e}"
        return None

    def enterprise_grounding_api_call(self, prompt: str) -> str:
        """Retrieves any financial information for any company using a special Grounding API.

        Args:
            prompt (str): The query or prompt from the agent to retrieve the financial information.
        """
        try:
            gcp_access_token = self.get_gcp_access_token()
            print(gcp_access_token)
            access_token = self.get_access_token()
            print(access_token)
            headers = {"Authorization": f"Bearer {gcp_access_token}", "Accept": "Application"}

            data = {
                "location": f"projects/214453227823/locations/global",
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationSpec": {"modelId": f"gemini-2.5-flash"},
                "groundingSpec": {
                    "groundingSources": [
                        {
                            "apiSource": {
                                "manifest": {
                                    "endpoint": "https://grounding.preview.kensho.com/v0/gcp_grounding/",
                                    "authConfig": {
                                        "apiKeyConfig": {
                                            "name": "Authorization",
                                            "apiKeyString": f"Bearer {access_token}",
                                            "httpElementLocation": "HTTP_IN_HEADER",
                                        }
                                    },
                                }
                            }
                        }
                    ]
                },
            }
            start_time = time.time()
            response = requests.post(
                f"https://discoveryengine.googleapis.com/v1/projects/214453227823/locations/global:generateGroundedContent",
                headers=headers,
                data=json.dumps(data),
            )
            response.raise_for_status()  # Raise HTTPError for bad responses
            print(f"Time: {time.time() - start_time}")
            result = response.json()
            content = [part["text"] for part in result["candidates"][0]["content"]["parts"]]
            sources = result["candidates"][0]["groundingMetadata"].get("supportChunks",[])
            return str({"content": content, "sources": sources})

        except Exception as e:
            print(f"There was an error: {e}")
            return str({"error": e})