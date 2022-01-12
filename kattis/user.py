from re import sub
import requests

from typing import Tuple, List

from .doc_parser import (
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
        self._auth(username, password)
    
    
    def stats(self) -> Tuple[int, float]:
        """Gets the rank and score of the user.

        Returns:
            rank and score of the user.
        """
        url = f'{KATTIS_URL}/users/{self._username}'
        res = self._session.get(url)
        rank, score = get_rank_score(res.text)
        return rank, score
    
    
    def solved_problems(self) -> List[ProblemData]:
        """Gets the list of all problems solved by the user.

        Returns:
            all solved problems' data by the user.
        """
        url = f'{KATTIS_URL}/problems?show_solved=on&show_tried=off&show_untried=off'
        page_id = 0

        problem_list = []
        while True:
            res = self._session.get(f'{url}&page={page_id}')
            page_problems = get_page_problems(res.text)
            problem_list.extend(page_problems)
            if len(page_problems) == 0:
                break
            page_id += 1
        print('Got all problems!')
        
        print('Retrieving solve dates...')
        for i in range(len(problem_list)):
            print(f'{i+1}/{len(problem_list)}')
            problem_list[i]['solve_date'] = (
                self.solve_date(problem_list[i]['id']))
            
        return problem_list


    def submissions(self, problem_id: str) -> List[SubmissionData]:
        """Get submission data of a given problem.

        Args:
            problem_id: the problem ID to query
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


    def _auth(self, username: str, password: str) -> requests.Response:
        """Logs a user into the site.

        Args:
            username: email credential to authenticate.
            password: password credential to authenticate.

        Returns:
            the HTTP POST response after authenticating user.
        """
        # TODO: check if auth was successful/unsuccessful

        url = f'{KATTIS_URL}/login/email'
        res = self._session.get(url)
        payload = {
            'user': username,
            'password': password,
            'csrf_token': get_csrf_token(res.text),
            'submit': 'Submit'
        }
        res = self._session.post(url, data=payload)
        return res
    