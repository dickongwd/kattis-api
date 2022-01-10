import os
import requests

from base64 import b64decode
from bs4 import BeautifulSoup

# For weak certificates. Comment if not needed.
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = "ALL:@SECLEVEL=1"

LOGIN_URL = "https://open.kattis.com/login/email"
USER_CREDENTIALS = {
    "user": os.environ.get("KATTIS_USER"),
    "password": b64decode(os.environ.get("KATTIS_PASS")
        .encode("utf-8"))
        .decode("utf-8")
}


def get_csrf_token(res: requests.request) -> str:
    """Parses a HTTP GET Response to obtain the generated CSRF token.
    The CSRF token is hidden as in the form
        <input type="hidden" name="csrf_token" value="<token>">
    Args:
        res: the HTTP GET response to parse.
    Returns:
        the CSRF token as a string.
    """
    # TODO: errors/checks for valid response, or if csrf token is not present

    soup = BeautifulSoup(res.content, "html.parser")
    return soup.find("input", {"name": "csrf_token"})["value"]


def auth(sess: requests.Session) -> requests.Response:
    """Logs a user into the site.
    Args:
        sess: a request session
    
    Returns:
        the HTTP POST response after authenticating user
    """
    # TODO: check if auth was successful/unsuccessful

    res = sess.get(LOGIN_URL)
    payload = USER_CREDENTIALS
    payload["csrf_token"] = get_csrf_token(res)
    payload["submit"] = "Submit"
    res = sess.post(LOGIN_URL, data=payload)
    return res


def main():
    with requests.Session() as sess:
        # WIP
        res = auth(sess)
        with open("test.html", "wb") as f:
            f.write(res.content)


if __name__ == "__main__":
    main()
