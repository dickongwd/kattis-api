import os

from base64 import b64decode
from tqdm import tqdm

from kattis.user import KattisUser
from notion.notion import Notion

NOTION_DATABASE_ID = "05b8074c2b394663920fd14b635e50c7"


def main():
    username = os.environ.get('KATTIS_USER')
    password = b64decode(os.environ.get('KATTIS_PASS')
                .encode('utf-8')).decode('utf-8')
    notion_api_key = os.environ.get('NOTION_API_KEY')

    notion = Notion(notion_api_key)
    
    print('Authenticating Kattis...')
    user = KattisUser(username, password)
    print('Logged in successfully!')

    with open('solve.txt', 'w') as fp:
        for problem in tqdm(user.solved_problems(), desc='Querying problems',
                            total=user.problem_count()):
            fp.write(str(problem))
            fp.write('\n')
            notion.create_page(NOTION_DATABASE_ID, 
                               problem['name'], problem['solve_date'],
                               problem['id'], problem['difficulty'])
    print('Update done!')

     
if __name__ == '__main__':
    main()
