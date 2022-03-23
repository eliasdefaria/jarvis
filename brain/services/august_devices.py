import asyncio
from multiprocessing.sharedctypes import Value
from os import path 
from august.api import Api 
from august.authenticator import Authenticator, AuthenticationState


async def init_august_devices() -> None:
    root_dir = path.dirname(path.abspath(__file__))
    august_token_file_path = path.join(root_dir.split('brain/')[0], 'infra/auth/august_access_token.json')
    if not path.exists(august_token_file_path):
        raise ValueError(f'\n\nCritical error initializing August devices. No token file found at {august_token_file_path}/ Aborting initialization...\n\n')
    
    api = Api(timeout=20)
    authenticator = Authenticator(api, "email", "", "", access_token_cache_file=august_token_file_path)

    authentication = authenticator.authenticate()

    if authentication.state != AuthenticationState.AUTHENTICATED:
        raise ValueError('Critical error initializing August devices. Authentication tokens expired or invalid. Please run the script to replace them. Aborting...')
    
    print('Successfully authenticated with August. Initializing devices...')

if __name__ == '__main__':
    asyncio.run(init_august_devices())