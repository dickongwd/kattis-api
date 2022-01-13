"""
notion.notion
-------------

Provides helper functions as an interface to the Notion API.
This module is created specifically for a specific Notion table database schema:
    (Name: title, Date: date, ID: text, Difficulty: number)
"""
import json
import time
import requests

from .constants import NOTION_API_URL


class Notion:
    """Represents a Notion integration.

    Attributes:
        _api_key: Notion API key of the integration
    """
    def __init__(self, api_key):
        self._api_key = api_key
    
    
    def create_page(self, database_id: str, name: str, date: str, id: str,
                    difficulty: float):
        """Creates a page (or entry) in the Notion database.

        Each entry represents each solved Kattis problem.

        Args:
            database_id: ID of database to create page at
            name: name of solved Kattis problem
            date: earliest date problem was solved
            id: Kattis problem ID
            difficulty: difficulty/score of problem

        Returns:
            True if the creation was successful. False otherwise.
        """
        post_data = {
            'parent': {'database_id': database_id},
            'properties': {
                'Name': {
                    'title': [
                        {
                            'text': {
                                'content': name
                            }
                        }
                    ]
                },
                'Date': {
                    'date': {
                        'start': date
                    }
                },
                'ID': {
                    'rich_text': [
                        {
                            'type': 'text',
                            'text': {'content': id}
                        }
                    ]
                },
                'Difficulty': {
                    'number': difficulty
                }
            }
        }
        res = requests.post(
            f'{NOTION_API_URL}/pages',
            headers={
                'Authorization': f'Bearer {self._api_key}',
                'Content-Type': 'application/json',
                'Notion-Version': '2021-08-16'
            },
            data=json.dumps(post_data)
        )
        json_reply = json.loads(res.content.decode('utf-8'))

        if res.status_code == 200 and json_reply['object'] == 'page':
            return True
        # Rate Limit
        elif res.status_code == 429:
            time.sleep(1)
            return self.create_page(name, date)
        else:
            return False
