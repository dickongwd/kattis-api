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
