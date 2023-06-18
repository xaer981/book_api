import base64
import os

from dotenv import load_dotenv

load_dotenv()


def encode_credentials(credentials: bytes):

    return base64.b64encode(credentials)


if __name__ == '__main__':
    username = os.getenv('ADMIN_USER')
    password = os.getenv('ADMIN_PASSWORD')

    credentials = bytes(':'.join([username, password]), 'utf8')

    print(encode_credentials(credentials).decode())
