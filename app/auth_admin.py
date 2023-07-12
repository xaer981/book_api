import os
import secrets
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

load_dotenv()

security = HTTPBasic()


def check_admin(credentials: Annotated[HTTPBasicCredentials,
                                       Depends(security)]):
    """
    Compare credentials with credentials in .env file.

    Args:
        credentials: contains username and password.

    Raises:
        HTTPException: username or password incorrect.
    """
    current_username = credentials.username.encode('utf8')
    correct_username = os.getenv('ADMIN_USER').encode('utf8')
    is_correct_username = secrets.compare_digest(current_username,
                                                 correct_username)

    current_password = credentials.password.encode('utf8')
    correct_password = os.getenv('ADMIN_PASSWORD').encode('utf8')
    is_correct_password = secrets.compare_digest(current_password,
                                                 correct_password)

    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect admin username or password',
            headers={'WWW-Authenticate': 'Basic'}
        )
