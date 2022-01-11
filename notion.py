import os
import json
import time
import requests

# For weak certificates. Uncomment if needed.
# requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = "ALL:@SECLEVEL=1"

NOTION_API_URL = "https://api.notion.com/v1/pages"

NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
NOTION_DATABASE_ID = os.environ.get("NOTION_DATABSE_ID")


def create_page(name: str, date: str):
    """Creates a page (or entry) in the Notion database.

    Each entry represents each solved Kattis problem.
    Notion database schema - (Name: title, Date: date)

    Args:
        name: name of solved Kattis problem
        date: earliest date problem was solved

    Returns:
        True if the creation was successful. False otherwise.

    """
    # TODO: respond to different response status code
    # e.g. 429 - too high rate of requests

    post_data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": name
                        }
                    }
                ]
            },
            "Date": {
                "date": {
                    "start": date
                }
            }
        }
    }
    res = requests.request(
        "POST",
        NOTION_API_URL,
        headers={
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Content-Type": "application/json",
            "Notion-Version": "2021-08-16"
        },
        data=json.dumps(post_data)
    )
    json_reply = json.loads(res.content.decode("utf-8"))

    if res.status_code == 200 and json_reply["object"] == "page":
        return True
    # Rate Limit
    elif res.status_code == 429:
        time.sleep(1)
        return create_page(name, date)
    else:
        return False


def main():
    # WIP
    create_page("testname", "2021-01-11")


if __name__ == "__main__":
    main()
