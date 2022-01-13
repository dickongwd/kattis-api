"""
kattis.user
-----------

This module provides functionality for Kattis users to retrieve their data.
"""
import requests

from typing import Tuple, Iterator, Dict

from .doc_parser import (
    contains_user_info,
    get_csrf_token,
    get_rank_score,
    get_page_problems,
    get_page_submissions,
    ProblemData,
    SubmissionData
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
        if not self._auth(username, password):
            raise AuthError('Failed to authenticate with Kattis')
    
    
    def stats(self) -> Tuple[int, float]:
        """Gets the rank and score of the user.

        Returns:
            rank and score of the user.
        """
        url = f'{KATTIS_URL}/users/{self._username}'
        res = self._session.get(url)
        rank, score = get_rank_score(res.text)
        return rank, score
    
    
    def solved_problems(self) -> Iterator[ProblemData]:
        """Gets the list of all problems solved by the user.

        Returns:
            all solved problems' data by the user.
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
            

    def submissions(self) -> Iterator[SubmissionData]:
        """Get submission data of a given problem.

        Args:
            problem_id: the problem ID to query.
        
        Returns:
            all user submissions.
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
            the HTTP POST response after authenticating user.
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
        return contains_user_info(res.text)


class AuthError(Exception):
    pass
    