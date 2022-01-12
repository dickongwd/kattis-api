import requests

from typing import Tuple

from .utils import get_csrf_token, get_rank_score
from .constants import KATTIS_URL


class KattisUser:
    """Represents an authenticated Kattis user.

    Attributes:
        _username: username of the user.
        _session: a requests session to provide logged in persistence.
    """
    def __init__(self, username, password):
        self._username = username
        self._session = requests.Session()
        # TEMP
        self._auth(username, password)
    
    
    def _auth(self, username: str, password: str) -> requests.Response:
        """Logs a user into the site.

        Args:
            username: email credential to authenticate.
            password: password credential to authenticate.

        Returns:
            the HTTP POST response after authenticating user.
        """
        # TODO: check if auth was successful/unsuccessful

        login_url = f'{KATTIS_URL}/login/email'
        res = self._session.get(login_url)
        payload = {
            'user': username,
            'password': password,
            'csrf_token': get_csrf_token(res.content.decode('utf-8')),
            'submit': 'Submit'
        }
        res = self._session.post(login_url, data=payload)
        return res
