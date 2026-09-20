"""Support connection to https://put.io/."""

from enum import Enum

from pydantic import BaseModel
import httpx


class PutIOTransfer(BaseModel):
    """A Transfer object from the PutIO API."""

    class PutIOTransferStatus(str, Enum):
        """The different transfer statuses returned by PutIO.

        A download is finished if it has the status "COMPLETED" or "SEEDING".
        """

        IN_QUEUE = "IN_QUEUE"
        WAITING = "WAITING"
        PREPARING_DOWNLOAD = "PREPARING_DOWNLOAD"
        DOWNLOADING = "DOWNLOADING"
        COMPLETING = "COMPLETING"
        SEEDING = "SEEDING"
        COMPLETED = "COMPLETED"
        ERROR = "ERROR"

    id: int
    status: PutIOTransferStatus


class NeppyPutIOClient:
    """A Client for put.io, a site for handling torrents."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        putio_username: str,
        putio_password: str,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.putio_username = putio_username
        self.putio_password = putio_password

    def add_transfer(self, magnet_link: str) -> PutIOTransfer:
        with httpx.Client() as http_client:
            access_token = self._generate_putio_access_token(http_client)
            response = http_client.post(
                "https://api.put.io/v2/transfers/add",
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Authorization": f"token {access_token}",
                },
                data={"url": magnet_link},
            )
        response_json = response.json()
        transfer_data = response_json["transfer"]
        return PutIOTransfer(**transfer_data)

    def get_transfer(self, transfer_id: str) -> PutIOTransfer:
        with httpx.Client() as http_client:
            access_token = self._generate_putio_access_token(http_client)
            response = http_client.post(
                f"https://api.put.io/v2/transfers/{transfer_id}",
                headers={"Authorization": f"token {access_token}"},
            )
        response_json = response.json()
        transfer_data = response_json["transfer"]
        return PutIOTransfer(**transfer_data)

    def _generate_putio_access_token(self, http_client: httpx.Client) -> str:
        """Generates and returns a put.io API access token."""
        data = {"client_secret": self.client_secret}
        auth = (self.putio_username, self.putio_password)
        url = f"https://api.put.io/v2/oauth2/authorizations/clients/{self.client_id}/?grant_type=client_credentials"
        response = http_client.put(url, data=data, auth=auth)
        return response.json()["access_token"]
