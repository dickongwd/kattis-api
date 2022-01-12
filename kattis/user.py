import requests

from typing import Tuple, Iterator

from .doc_parser import get_csrf_token, get_rank_score, get_page_problems, ProblemInfo
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
    
    
    def get_stats(self) -> Tuple[int, int]:
        """Gets the rank and score of the user.

        Returns:
            rank and score of the user.
        """
        user_url = f'{KATTIS_URL}/users/{self._username}'
        res = self._session.get(user_url)
        rank, score = get_rank_score(res.content.decode('utf-8'))
        return rank, score
    
    
    def get_solved_problems(self) -> Iterator[ProblemInfo]:
        """Gets the list of all problems solved by the user.

        Returns:
            all solved problems by the user.
        """
        problem_list_url = f'{KATTIS_URL}/problems?show_solved=on&show_tried=off&show_untried=off'
        page_id = 0
        while True:
            res = self._session.get(f'{problem_list_url}&page={page_id}')
            problem_list = get_page_problems(res.content.decode('utf-8'))
            for problem_info in problem_list:
                yield problem_info

            if len(problem_list) == 0:
                break
            page_id += 1


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
    