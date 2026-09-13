"""Types used or returned by the Google client."""

import datetime as dt

from utils import neppy_dataclass


@neppy_dataclass
class ListMessagesOptions:
    """Search options.

    Attributes:
        received_after (dt.datetime, optional): filter that includes messages sent after this timestamp
        with_label_id (str, optional): filter for messages that include the input label. Default: "INBOX"
        with_any_label_ids (list[str], optional): filter for messages that include one of the input labels
        with_all_label_ids (list[str], optional): filter for messages that include all of the input labels
    """

    received_after: dt.datetime | None = None
    with_label_id: str | None = "INBOX"
    with_any_label_ids: list[str] | None = None
    with_all_label_ids: list[str] | None = None


@neppy_dataclass
class ListMessagesResult:
    """Result of ``NeppyGoogleClient.list_gmail_messages(...)``."""

    messages: list[Message]
    next_page_token: str | None


@neppy_dataclass
class Message:
    """An individual Gmail Message."""

    id: str
    thread_id: str
    utc_timestamp: dt.datetime
    label_ids: list[str]

    sender: str
    subject: str | None
    content: str
