import neppy_config
from integrations.google import NeppyGoogleService


def main():
    print("Starting Neppy")

    credentials = NeppyGoogleService(neppy_config.google_secret_path)


if __name__ == "__main__":
    main()
