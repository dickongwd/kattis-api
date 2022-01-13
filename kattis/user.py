"""
kattis.user
-----------

This module provides functionality for Kattis users to retrieve their data.
"""
import requests

from typing import Tuple, List, Iterator

from .doc_parser import (
    contains_user_info,
    get_csrf_token,
    get_rank_score,
    get_page_problems,
    get_page_submissions,
    get_page_problem_count,
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
                problem['solve_date'] = self.solve_date(problem['id'])
                yield problem

            if empty_page:
                break
            page_id += 1
    

    def solve_date(self, problem_id: str) -> str:
        """Get the date of the first accepted solve for a given problem.
        
        Args:
            problem_id: the problem ID to query

        Returns:
            date of earliest accepted submission, 'YYYY-MM-DD'
        """
        submissions = self.submissions(problem_id)
        submissions = list(filter(lambda s : s['accepted'], submissions))
        submissions.reverse()
        if len(submissions) == 0:
            return None
        return submissions[0]['date'].strftime('%Y-%m-%d')


    def submissions(self, problem_id: str) -> List[SubmissionData]:
        """Get submission data of a given problem.

        Args:
            problem_id: the problem ID to query
        
        Returns:
            list of user submissions
        """
        url = f'https://open.kattis.com/users/{self._username}/submissions/{problem_id}'
        page_id = 0

        submissions = []
        while True:
            res = self._session.get(f'{url}?page={page_id}')
            page_submissions = get_page_submissions(res.text)
            submissions.extend(page_submissions)
            if len(page_submissions) == 0:
                break
            page_id += 1
        return submissions
    
    
    def problem_count(self) -> int:
        """Gets the total number of solved problems.

        Returns:
            number of solved problems.
        """
        url = f'{KATTIS_URL}/problems?show_solved=on&show_tried=off&show_untried=off'
        total = 0
        page_id = 0

        while True:
            res = self._session.get(f'{url}&page={page_id}')
            page_count = get_page_problem_count(res.text)
            total += page_count
            if page_count == 0:
                break
            page_id += 1
        return total


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
    