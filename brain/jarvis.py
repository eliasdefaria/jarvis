import asyncio

from db.db import JarvisStatus

from models.status import Status
from services.kasa_devices import init_kasa_devices

# TODO: Add try / except for error handling with devices
# TODO: Write a test!
# TODO: Build voice processing
# TODO: Investigate flask secret key purpose

def init_jarvis() -> None:
    init_brain()
    init_devices()
    

def init_brain() -> None:
    if JarvisStatus.select().count() > 0:
        return
    
    print('Initializing brain...')
    JarvisStatus.create(status=Status.ON.value)
    print('Brain initialized... \nHello sir. Give me just a moment to check in on the house...')
    
def init_devices() -> None:
    asyncio.run(init_kasa_devices())

if __name__ == '__main__':
    init_jarvis()