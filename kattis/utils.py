from bs4 import BeautifulSoup
from typing import Tuple


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
    """Parses a HTML document string to obtain the rank and score of the Kattis user.

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
