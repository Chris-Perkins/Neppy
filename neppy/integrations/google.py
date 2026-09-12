import json

import cache
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials as GoogleCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

_REQUIRED_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
_AUTH_CACHE_KEY = "auth/google"
"""Where cached auth credentials are stored"""


class NeppyGoogleService:
    """
    Neppy-based Google Client with access to Gmail
    """

    def __init__(self, client_secret_file_path: str):
        creds: GoogleCredentials | None = None

        cached_auth_token_str = cache.get_value(_AUTH_CACHE_KEY)
        if cached_auth_token_str is not None:
            cached_auth_token = json.loads(cached_auth_token_str)
            creds = GoogleCredentials.from_authorized_user_info(cached_auth_token, _REQUIRED_SCOPES)

        should_refresh_credentials = creds is not None and creds.expired and creds.refresh_token
        if should_refresh_credentials:
            creds.refresh(Request())

        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file_path, _REQUIRED_SCOPES)
            creds = flow.run_local_server(port=0)

        self._gmail_client = build("gmail", "v1", credentials=creds)

        creds_str: str = creds.to_json()
        cache.set_value(_AUTH_CACHE_KEY, creds_str)

    def read_gmail_emails(self, max_results: int | None):
        results = self._gmail_client.users().messages().list(userId="me", labelIds=["INBOX"], maxResults=max_results).execute()
        messages = results.get("messages", [])

        email_data = []
        if not messages:
            print("No messages found.")
        else:
            for message in messages:
                msg = self._gmail_client.users().messages().get(userId="me", id=message["id"]).execute()

                # Extract Subject
                headers = msg["payload"]["headers"]
                subject = next(
                    (header["value"] for header in headers if header["name"] == "Subject"),
                    "No Subject",
                )
                snippet = msg.get("snippet", "")

                email_data.append(f"Subject: {subject}\nSnippet: {snippet}")

        return email_data
