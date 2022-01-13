"""
kattis.doc_parser
-----------------

This module provides helper functions for parsing of the HTML document
obtained from scraping the Kattis site.
"""
import re

from bs4 import BeautifulSoup
from typing import Tuple, TypedDict, List
from datetime import datetime


class ProblemData(TypedDict):
    id: str
    name: str
    difficulty: float
    solve_date: str


class SubmissionData(TypedDict):
    id: int
    date: datetime
    accepted: bool


def get_csrf_token(html_doc: str) -> str:
    """Parses a HTML document string to obtain the generated CSRF token.

    The CSRF token is hidden in the form:
        <input type="hidden" name="csrf_token" value="<token>">

    Args:
        html_doc: the HTML document to parse.

    Returns:
        the CSRF token as a string.
    """
    # TODO: errors/checks for valid response, or if csrf token is not present

    soup = BeautifulSoup(html_doc, 'html.parser')
    return soup.find('input', {'name': 'csrf_token'})['value']


def get_rank_score(html_doc: str) -> Tuple[int, float]:
    """Parses a HTML document string to obtain the rank and score of the user.

    The table holding the rank and score is assumed to be of the form:
        <div class="rank clearfix">
            <table>
                <tr>
                    <td>
                        <span>Rank</span>
                    </td>
                    <td>
                        <span>Score</span>
                    </td>
                </tr>
                <tr>
                    <td>
                        229
                    </td>
                    <td>
                        1400.0
                    </td>
                </tr>
            </table>
        </div>
    
    Args:
        html_doc: the HTML document to parse.

    Returns:
        the rank and score of the user
    """
    soup = BeautifulSoup(html_doc, 'html.parser')
    table = soup.find('div', class_='rank')
    strings = list(table.stripped_strings)
    return int(strings[2]), float(strings[3])


def get_page_problems(html_doc: str) -> List[ProblemData]:
    """Parses a HTML document string to obtain the displayed list of problems.
    
    The table holding the list of problems is assumed to have:
        <table class="problem_list ...">
    Schema for the table is:
        (NAME, TOTAL, ACC., RATIO, FASTEST, TOTAL, ACC. RATIO, DIFFICULTY)

    Args:
        html_doc: the HTML document to parse.

    Returns:
        all solved problems' data in the given page.
    """
    soup = BeautifulSoup(html_doc, 'html.parser')
    table_body = soup.find('table', class_='problem_list').find('tbody')
    rows = table_body.find_all('tr')

    for row in rows:
        # Get problem unique id
        href_link = row.find('td', class_='name_column').find('a')['href']
        id = re.match(r'/problems/(.+)', href_link).group(1)

        # Get other stats
        row_data = list(row.stripped_strings)
        name = row_data[0]
        difficulty = row_data[-1]
        if '-' in difficulty:
            difficulty = difficulty.split()[-1]
        difficulty = float(difficulty)

        yield {
            'id': id,
            'name': name,
            'difficulty': difficulty,
            'solve_date': ''
        }


def get_page_submissions(html_doc: str) -> List[SubmissionData]:
    """Parses a HTML document string to obtain submission data for a problem.

    Table holding submissions data is assumed to have:
        <table class="table-submissions ...">
    Schema for the table is:
        (ID, DATE, PROBLEM, STATUS, CPU, LANG)

    Args:
        html_doc: the HTML document to parse.


    Returns:
        list of all submissions for a given problem
    """
    soup = BeautifulSoup(html_doc, 'html.parser')
    table_body = soup.find('table', class_='table-submissions').find('tbody')
    rows = table_body.find_all('tr')

    submissions = []
    for row in rows:
        # Get submission stats
        row_data = list(row.stripped_strings)
        id = row_data[0]
        date = datetime.fromisoformat(row_data[1])
        accepted = True if 'Accepted' in row_data[3] else False

        submissions.append({
            'id': id,
            'date': date,
            'accepted': accepted
        })
    return submissions


def get_page_problem_count(html_doc: str) -> int:
    """Gets the number of problems listed in a given HTML document.

    Args:
        html_doc: the HTML document to parse.
    
    Returns:
        the number of problems listed in the given page.
    """
    soup = BeautifulSoup(html_doc, 'html.parser')
    table_body = soup.find('table', class_='problem_list').find('tbody')
    return len(table_body.find_all('tr'))
