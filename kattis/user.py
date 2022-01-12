import requests

from typing import Tuple, List

from .doc_parser import (
    get_csrf_token,
    get_rank_score,
    get_page_problems,
    ProblemData
)
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
        self._auth(username, password)
    
    
    def stats(self) -> Tuple[int, float]:
        """Gets the rank and score of the user.

        Returns:
            rank and score of the user.
        """
        user_url = f'{KATTIS_URL}/users/{self._username}'
        res = self._session.get(user_url)
        rank, score = get_rank_score(res.content.decode('utf-8'))
        return rank, score
    
    
    def solved_problems(self) -> List[ProblemData]:
        """Gets the list of all problems solved by the user.

        Returns:
            all solved problems' data by the user.
        """
        problem_list_url = f'{KATTIS_URL}/problems?show_solved=on&show_tried=off&show_untried=off'
        page_id = 0

        problem_list = []
        while True:
            res = self._session.get(f'{problem_list_url}&page={page_id}')
            page_problems = get_page_problems(res.content.decode('utf-8'))
            problem_list.extend(page_problems)
            if len(page_problems) == 0:
                break
            page_id += 1
        return problem_list


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
    