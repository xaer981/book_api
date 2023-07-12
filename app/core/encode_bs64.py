import base64
import os

from dotenv import load_dotenv

load_dotenv()


def encode_credentials(credentials: bytes):
    """
    Encoding credentials to base64
    for using in basic auth(e.g. in postman).

    Args:
        credentials (bytes): credentials (username password).

    Prints:
        Encoded credentials.
    """

    return base64.b64encode(credentials)


if __name__ == '__main__':
    username = os.getenv('ADMIN_USER')
    password = os.getenv('ADMIN_PASSWORD')

    credentials = bytes(':'.join([username, password]), 'utf8')

    print(encode_credentials(credentials).decode())
