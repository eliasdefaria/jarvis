# TODO: Upload credentials to github secrets with github secrets api (https://docs.github.com/en/rest/reference/actions#secrets)

from august.api import Api 
from august.authenticator import Authenticator, AuthenticationState
from os import path

root_dir = path.dirname(path.abspath(__file__))
target_dir = path.join(root_dir.split('scripts/')[0], 'auth/august_access_token.json')

email = input('Please input your August Account Email: ')
pwd = input('Please input your August account pwd: ')

api = Api(timeout=20)
authenticator = Authenticator(api, "email", email, pwd, access_token_cache_file=target_dir)


authentication = authenticator.authenticate()

if authentication.state == AuthenticationState.REQUIRES_VALIDATION:
    authenticator.send_verification_code()
    code = input('Please input the verification code: ')
    authenticator.validate_verification_code(code)
elif authentication.state == AuthenticationState.BAD_PASSWORD:
    print('Email or password was incorrect. Aborting...')
    exit()
elif authentication.state == AuthenticationState.AUTHENTICATED:
    print(f'User with email {email} already authenticated')
    exit()

authentication = authenticator.authenticate()

if authentication.state == AuthenticationState.AUTHENTICATED:
    print(f'Successfully authenticated user: {email}')