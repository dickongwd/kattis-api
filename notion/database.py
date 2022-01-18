"""
notion.database
-------------

Provides helper functions as an interface to the Notion API.
This module is created specifically for a specific Notion table database schema:
    (Name: title, Date: date, ID: text, Difficulty: number)
"""
import json
import time
from typing import List, TypedDict
import requests

from .constants import NOTION_API_URL

class Problem(TypedDict):
    """Represents a solved problem and contains its data."""
    # Name of solved Kattis problem
    name: str

    # Earliest date problem was solved
    date: str

    # Problem ID
    id: str

    # Problem difficulty/score
    difficulty: float


class Notion:
    """Represents a Notion integration.

    Attributes:
        _api_key: Notion API key of the integration.
        _database_id: Database ID of the database to update. 
    """
    def __init__(self, api_key, database_id):
        self._api_key = api_key
        self._database_id = database_id
    

    def update(self, new_problems: List[Problem]) -> List[Problem]:
        """Updates the Notion database.

        Compares data obtained from Notion with the new problem list
        to fill up the difference.

        Args:
            new_problems: Updated list of solved problems.

        Returns:
            List of problems updated.
        """
        old_ids = {p['id'] for p in self.query()}
        new_ids = {p['id'] for p in new_problems}

        updated_ids = new_ids.difference(old_ids)
        updated_problems = []
        for p in new_problems:
            if p['id'] in updated_ids:
                self.add(p)
                updated_problems.append(p)
                print('Updated', p['id'])
        return updated_problems
            

    def add(self, problem: Problem) -> None:
        """Adds a page (or entry) in the Notion database.

        Each entry represents each solved Kattis problem.

        Args:
            problem: Data of the solved problem.

        Returns:
            None
        
        Raises:
            NotionAPIError: If Notion API create page was unsuccessful.
        """
        post_data = {
            'parent': {'database_id': self._database_id},
            'properties': {
                'Name': {
                    'title': [
                        {
                            'text': {
                                'content': problem['name']
                            }
                        }
                    ]
                },
                'Date': {
                    'date': {
                        'start': problem['date']
                    }
                },
                'ID': {
                    'rich_text': [
                        {
                            'type': 'text',
                            'text': {'content': problem['id']}
                        }
                    ]
                },
                'Difficulty': {
                    'number': problem['difficulty']
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
        json_res = json.loads(res.text)

        # Rate Limit
        if res.status_code == 429:
            time.sleep(1)
            self.add(problem)
        elif not (res.status_code == 200 and json_res['object'] == 'page'):
            raise NotionAPIError('Notion create page failed')


    def query(self, start_cursor: str = None) -> List[Problem]:
        """Queries a Notion database to acquire list of solved problems.

        Args:
            start_cursor: Start point of query, specific to Notion API.

        Returns:
            List of solved problems.
        
        Raises:
            NotionAPIError: If Notion API database query was unsuccessful.
        """
        problems = []

        post_data = {}
        if start_cursor:
            post_data['start_cursor'] = start_cursor

        res = requests.post(
            f'{NOTION_API_URL}/databases/{self._database_id}/query',
            headers={
                'Authorization': f'Bearer {self._api_key}',
                'Content-Type': 'application/json',
                'Notion-Version': '2021-08-16'
            },
            data=json.dumps(post_data)
        )
        json_res = json.loads(res.text)

        # Rate Limit
        if res.status_code == 429:
            time.sleep(1)
            return self.query(start_cursor)
        elif not (res.status_code == 200 and json_res['object'] == 'list'):
            raise NotionAPIError('Notion database query failed')

        for page in json_res['results']:
            properties = page['properties']
            problems.append({
                'name': properties['Name']['title'][0]['text']['content'],
                'date': properties['Date']['date']['start'],
                'id': properties['ID']['rich_text'][0]['text']['content'],
                'difficulty': properties['Difficulty']['number']
            })
        
        if json_res['has_more']:
            problems.extend(
                self.query(start_cursor=json_res['next_cursor']))
        return problems


class NotionAPIError(Exception):
    pass
