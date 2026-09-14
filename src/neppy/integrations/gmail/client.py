"""Google Client with Gmail access."""

from email.message import EmailMessage
import base64
import datetime as dt
import json

from google.oauth2.credentials import Credentials as GoogleOAuthCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from requests import Request

from neppy.exceptions import InternalException
from neppy.utils.caching import get_cached_value, set_cached_value
import neppy.config

from .types import CreateDraftMessageResponse, Label, ListMessagesOptions, ListMessagesResult, Message

_REQUIRED_SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
]
_AUTH_CACHE_KEY = "auth/google"
"""Where cached auth credentials are stored"""


class NeppyGmailClient:
    """Neppy-based Google Client with access to Gmail."""

    def __init__(self, client_secret_file_path: str):
        """Initializes the Google client, refreshing credentials if necessary."""
        google_credentials = _generate_google_credentials(_REQUIRED_SCOPES)
        self._gmail_client = build("gmail", "v1", credentials=google_credentials)

    def list_messages(self, options: ListMessagesOptions | None = None, page_token: str | None = None) -> ListMessagesResult:
        """Returns Gmail messages matching the input parameters.

        Args:
            options (ListGmailMessagesOptions, optional): Used to filter which messages are read. If not specified, default filters are applied.
            page_token (str, optional): Used to fetch the next page of messages.
        """
        searchQuery = _convert_list_messages_options_to_search_query(options or ListMessagesOptions())
        results = self._gmail_client.users().messages().list(userId="me", q=searchQuery, maxResults=20, pageToken=page_token).execute()

        try:
            result_message_summaries = results["messages"]
            result_message_ids: list[str] = [message["id"] for message in result_message_summaries]
            result_next_page_token: str | None = results.get("nextPageToken")
        except KeyError as e:
            raise InternalException("Reading Gmail messages failed: an expected field was missing") from e

        return ListMessagesResult(
            messages=[self._get_message(message_id) for message_id in result_message_ids],
            next_page_token=result_next_page_token,
        )

    def add_label_to_message(self, message_id: str, label_name: str) -> None:
        """Adds a label to the input message."""
        label = self._get_or_create_label(label_name)
        body = {"addLabelIds": [label.id]}
        self._gmail_client.users().messages().modify(userId="me", id=message_id, body=body).execute()

    def create_draft_message(self, thread_id: str, content: str) -> CreateDraftMessageResponse:
        """Creates a draft message that can be sent later using ``send_draft_message``."""
        mime_message = EmailMessage()
        mime_message.set_content(content)

        encoded_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
        draft_body = {"message": {"threadId": thread_id, "raw": encoded_message}}
        result = self._gmail_client.users().drafts().create(userId="me", body=draft_body).execute()
        return CreateDraftMessageResponse(draft_message_id=result["id"])

    def send_draft_message(self, draft_message_id: str) -> None:
        """Sends the input draft message."""
        self._gmail_client.users().drafts().send(userId="me", body={"id": draft_message_id}).execute()

    def _get_or_create_label(self, label_name: str) -> Label:
        """Finds a label by name, creating it if it doesn't exist, and returns its ID."""
        labels = self._get_labels()
        label_with_name = next((label for label in labels if label.name.lower() == label_name.lower()), None)
        if label_with_name:
            return label_with_name

        label_body = {"name": label_name, "labelListVisibility": "labelShow", "messageListVisibility": "show"}
        created_label = self._gmail_client.users().labels().create(userId="me", body=label_body).execute()
        return created_label["id"]

    def _get_labels(self) -> list[Label]:
        output: list[Label] = []

        label_results: list[dict] = self._gmail_client.users().labels().list(userId="me").execute()
        for label_result in label_results:
            label_id = label_result["id"]
            label_name = label_result["name"]
            output.append(Label(id=label_id, name=label_name))

        return output

    def _get_message(self, message_id: str) -> Message:
        result = self._gmail_client.users().messages().get(userId="me", id=message_id, format="full").execute()

        try:
            thread_id: str = result["threadId"]
            message_unix_epoch_ms: int = int(result["internalDate"])
            message_utc_timestamp: dt.datetime = dt.datetime.fromtimestamp(message_unix_epoch_ms / 1000, tz=dt.timezone.utc)
            label_ids: list[str] = result["labelIds"]

            result_payload: dict = result["payload"]
            result_payload_headers = result_payload["headers"]
            sender: str = next(h["value"] for h in result_payload_headers if h["name"] == "From")
            subject: str | None = next((h["value"] for h in result_payload_headers if h["name"] == "Subject"), None)

            result_payload_parts: list[dict] = result_payload.get("parts", [])
            content_textonly_parts = [part for part in result_payload_parts if part["mimeType"] == "text/plain"]
            content_base64_parts: list[str] = [part["body"]["data"] for part in content_textonly_parts if "data" in part["body"]]
            converted_content: list[str] = [_safe_base64_decode_to_str(base64_str) or "UNREADABLE" for base64_str in content_base64_parts]
            content: str = "\n".join(converted_content)
        except Exception as e:
            raise InternalException("An error occurred when reading a Gmail message") from e

        return Message(
            id=message_id,
            thread_id=thread_id,
            utc_timestamp=message_utc_timestamp,
            label_ids=label_ids,
            sender=sender,
            subject=subject,
            content=content,
        )


def _safe_base64_decode_to_str(base64_str: str) -> str | None:
    try:
        b = base64.urlsafe_b64decode(base64_str)
        return b.decode()
    except Exception:
        return None


def _convert_list_messages_options_to_search_query(gso: ListMessagesOptions) -> str:
    filters = []
    if gso.received_after is not None:
        unixSecondsTimestamp = int(gso.received_after.timestamp())
        filters.append(f"after:{unixSecondsTimestamp}")

    if gso.with_label_id is not None:
        filters.append(f"label:{gso.with_label_id}")

    if gso.with_any_label_ids is not None:
        label_filters = [f"label:{label_id}" for label_id in gso.with_any_label_ids]
        contains_any_label_filter = " or ".join(label_filters)
        filters.append(f"({contains_any_label_filter})")

    if gso.with_all_label_ids is not None:
        label_filters = [f"label:{label_id}" for label_id in gso.with_all_label_ids]
        contains_all_labels_filter = " and ".join(label_filters)
        filters.append(f"({contains_all_labels_filter})")

    return " and ".join(filters)


def _generate_google_credentials(required_scopes: list[str]) -> GoogleOAuthCredentials:
    creds = None

    auth_token_cache_key = "google/auth-token.json"
    cached_auth_token_token = get_cached_value(auth_token_cache_key)
    if cached_auth_token_token is not None:
        json_token = json.loads(cached_auth_token_token)
        creds = GoogleOAuthCredentials.from_authorized_user_info(json_token, scopes=_REQUIRED_SCOPES)

    if creds and creds.refresh and creds.expired:
        creds.refresh(Request())
    elif not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(neppy.config.google_secret_file_path, required_scopes)
        creds = flow.run_local_server(port=0)

    result = creds.to_json()
    set_cached_value(auth_token_cache_key, result)
    return creds  # pyright: ignore[reportReturnType] - Google SDK reports multiple possible return types, but the type we get is guaranteed.
