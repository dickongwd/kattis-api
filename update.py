import os

from base64 import b64decode
from tqdm import tqdm

from kattis.user import KattisUser
from notion.database import Notion


def main():
    username = os.environ.get('KATTIS_USER')
    password = b64decode(os.environ.get('KATTIS_PASS')
               .encode('utf-8')).decode('utf-8')
    notion_api_key = os.environ.get('NOTION_API_KEY')
    notion_database_id = os.environ.get('NOTION_DATABASE_ID')

    notion = Notion(notion_api_key, notion_database_id)

    print('Logging in to Kattis...', end=' ', flush=True)
    user = KattisUser(username, password)
    print('logged in successfully!')

    # Querying submissions
    # Submission dates listed on Kattis are assumed to be descending order
    # Most recent submissions first
    solve_dates = {}
    for sub in tqdm(user.submissions(),
                    desc='Getting submissions',
                    unit='submissions'):
        if not sub['accepted']:
            continue
        solve_dates[sub['problem_id']] = sub['date']
    
    # Querying problems
    problems = []
    for p in tqdm(user.solved_problems(),
                  desc='Getting solved problems',
                  unit='problems'):
        if p['id'] not in solve_dates:
            continue
        problems.append({
            'name': p['name'],
            'date': solve_dates[p['id']],
            'id': p['id'],
            'difficulty': p['difficulty']
        })
    
    # Updating Notion table
    # Functionality is equivalent to Notion.update()
    # Re-written here to display progress bar
    for p in tqdm(notion.query_updates(problems),
                  desc='Updating Notion database',
                  unit='entry'):
        notion.add(p)
    print('Update done!')

     
if __name__ == '__main__':
    main()
