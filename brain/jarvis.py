import asyncio

from db.db import JarvisStatus

from models.status import Status
from services.kasa_devices import init_kasa_devices, lights_on

# TODO: Add try / except for error handling with devices
# TODO: Type all files 
# TODO: Write a test!

def init_jarvis():
    init_brain()
    init_devices()

    import os
    print(os.environ['AUTH_TOKEN'])
    

def init_brain():
    if JarvisStatus.select().count() > 0:
        return
    
    print('Initializing brain...')
    JarvisStatus.create(status=Status.ON.value)
    print('Brain initialized... \nHello sir. Give me just a moment to check in on the house...')
    
def init_devices():
    asyncio.run(init_kasa_devices())

if __name__ == '__main__':
    init_jarvis()