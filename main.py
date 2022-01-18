import os

from base64 import b64decode
from tqdm import tqdm

from kattis.user import KattisUser
from notion.database import Notion

NOTION_DATABASE_ID = '05b8074c2b394663920fd14b635e50c7'


def main():
    username = os.environ.get('KATTIS_USER')
    password = b64decode(os.environ.get('KATTIS_PASS')
                .encode('utf-8')).decode('utf-8')
    notion_api_key = os.environ.get('NOTION_API_KEY')

    notion = Notion(notion_api_key, NOTION_DATABASE_ID)

    print('Logging in to Kattis...', end=' ', flush=True)
    user = KattisUser(username, password)
    print('logged in successfully!')

    # Querying submissions
    # Submission dates listed on Kattis are assumed to be descending order
    # Most recent submissions first
    solve_dates = {}
    for sub in tqdm(user.submissions(),
                    desc='Querying submissions',
                    unit='submissions'):
        if not sub['accepted']:
            continue
        solve_dates[sub['problem_id']] = sub['date'].strftime('%Y-%m-%d')
    
    # Querying problems
    problems = []
    for p in tqdm(user.solved_problems(),
                  desc='Querying problems',
                  unit='problems'):
        if p['id'] not in solve_dates:
            continue
        problems.append({
            'name': p['name'],
            'date': solve_dates[p['id']],
            'id': p['id'],
            'difficulty': p['difficulty']
        })

    print('Updating Notion database...')
    notion.update(problems)
    print('Update done!')

     
if __name__ == '__main__':
    main()
