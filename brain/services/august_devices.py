import asyncio
from multiprocessing.sharedctypes import Value
from os import path 
from august.api import Api
from august.authenticator import Authenticator, AuthenticationState
from typing import Any

class AugustDevice:
    _api: Api
    # NOTE: Need any here since august api types access_token as obscure 'Unknown' type
    _access_token: Any
    # TODO: Build support for more locks in the future
    front_door_lock_id: str

    def __init__(self) -> None:
        self._api = Api()
        print('Authenticating with August...')
        asyncio.run(self._authenticate())
        print('Fetching devices...')
        asyncio.run(self._fetch_devices())

    async def _authenticate(self) -> None:
        root_dir = path.dirname(path.abspath(__file__))
        august_token_file_path = path.join(root_dir.split('brain/')[0], 'infra/auth/august_access_token.json')
        if not path.exists(august_token_file_path):
            raise ValueError(f'\n\nCritical error initializing August devices. No token file found at {august_token_file_path}/ Aborting initialization...\n\n')
        
        authenticator = Authenticator(self._api, "email", "", "", access_token_cache_file=august_token_file_path)
        authentication = authenticator.authenticate()

        if not authentication or authentication.state != AuthenticationState.AUTHENTICATED:
            raise ValueError('Critical error initializing August devices. Authentication tokens expired or invalid. Please run the script to replace them. Aborting...')
        
        self._access_token = authentication.access_token
        print('Successfully authenticated with August.')

    async def _fetch_devices(self) -> None:
        locks = self._api.get_locks(self._access_token)
        if len(locks) == 0:
            raise ValueError('Critical error initializing August devices. No locks found. Aborting...')

        # TODO: Build support for more locks in the future
        self.front_door_lock_id = locks[0].device_id
    
    async def lock(self) -> None:
        Api.lock(self._api, self._access_token, self.front_door_lock_id)
       
    async def unlock(self) -> None:
        Api.unlock(self._api, self._access_token, self.front_door_lock_id)


if __name__ == '__main__':
    AugustDevice()