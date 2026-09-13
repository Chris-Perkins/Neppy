"""Entry point of Neppy."""

from integrations.gmail import NeppyGmailClient

import neppy.config


def main():
    print("Starting Neppy")

    service = NeppyGmailClient(neppy.config.google_secret_file_path)
    x = service.list_messages()
    print(x)


if __name__ == "__main__":
    main()
