"""
kattis.user
-----------

This module provides functionality for Kattis users to retrieve their data.
"""
import requests

from typing import Tuple, Iterator

from .doc_parser import (
    contains_user_info,
    get_csrf_token,
    get_rank_score,
    get_page_problems,
    get_page_submissions,
    ProblemData,
    Submission
)
from .constants import KATTIS_URL


class KattisUser:
    """Represents an authenticated Kattis user.

    Attributes:
        _username: Username of the user.
        _session: A requests session to provide logged in persistence.
    """
    def __init__(self, username, password):
        self._username = username
        self._session = requests.Session()
        self._auth(username, password)
    
    
    def stats(self) -> Tuple[int, float]:
        """Gets the rank and score of the user.

        Returns:
            Rank and score of the user.
        """
        url = f'{KATTIS_URL}/users/{self._username}'
        res = self._session.get(url)
        rank, score = get_rank_score(res.text)
        return rank, score
    
    
    def solved_problems(self) -> Iterator[ProblemData]:
        """Gets the list of all problems solved by the user.

        Returns:
            All solved problems' data by the user.
        """
        url = f'{KATTIS_URL}/problems?show_solved=on&show_tried=off&show_untried=off'
        page_id = 0

        while True:
            empty_page = True

            res = self._session.get(f'{url}&page={page_id}')
            for problem in get_page_problems(res.text):
                empty_page = False
                yield problem

            if empty_page:
                break
            page_id += 1
            

    def submissions(self) -> Iterator[Submission]:
        """Get submission data of a given problem.
        
        Returns:
            All user submissions.
        """
        url = f'https://open.kattis.com/users/{self._username}'
        page_id = 0

        while True:
            empty_page = True

            res = self._session.get(f'{url}?page={page_id}')
            for sub in get_page_submissions(res.text):
                empty_page = False
                yield sub

            if empty_page:
                break
            page_id += 1
    

    def _auth(self, username: str, password: str) -> bool:
        """Logs a user into the site.

        Args:
            username: email credential to authenticate.
            password: password credential to authenticate.

        Returns:
            None.
        
        Raises:
            AuthError: If authentication was unsuccessful.
        """
        url = f'{KATTIS_URL}/login/email'
        res = self._session.get(url)
        payload = {
            'user': username,
            'password': password,
            'csrf_token': get_csrf_token(res.text),
            'submit': 'Submit'
        }
        res = self._session.post(url, data=payload)

        # Checking if authentication was successful
        res = self._session.get(KATTIS_URL)
        if not contains_user_info(res.text):
            raise AuthError(Exception)


class AuthError(Exception):
    pass
    