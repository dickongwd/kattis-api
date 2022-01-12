import os

from base64 import b64decode

from kattis.user import KattisUser


def main():
    username = os.environ.get('KATTIS_USER')
    password = b64decode(os.environ.get('KATTIS_PASS')
                .encode('utf-8')).decode('utf-8')
    
    print('Authenticating...')
    user = KattisUser(username, password)
    print('Logged in successfully!')

    print('Getting all solved problems...')
    all_problems = user.solved_problems()
    print('Done!')

    print('Writing to file...')
    with open('solve.txt', 'w') as fp:
        for data in all_problems:
            fp.write(str(data))
            fp.write('\n')
    print('All done!')




if __name__ == '__main__':
    main()
