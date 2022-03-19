from db.db import JarvisStatus

from models.status import Status
from services.kasa_devices import init_kasa_devices
from services.executor import Executor
from services.speech_detection import SpeechDetector

# TODO: Write a test!
# TODO: Investigate flask secret key purpose

def init_jarvis() -> None:
    executor = Executor()
    init_brain()
    init_devices(executor)
    init_ears(executor)

def init_brain() -> None:
    try:
        if JarvisStatus.select().count() > 0:
            ValueError('Brain already initialized')
    
        print('Initializing brain...')
        JarvisStatus.create(status=Status.ON.value)
        print('Brain initialized... \nHello sir. Give me just a moment to check in on the house...')
    except ValueError as err:
        print('Failed to init Jarvis brain with error', err, 'Aborting...')
    
    
def init_devices(executor: Executor) -> None:
    try:
        executor.execute_command_from_fn(init_kasa_devices)
    except ValueError as err:
        print('Failed to init devices to connect to with error', err, 'Aborting...')

def init_ears(executor: Executor) -> None:
    try:
        speech_detector = SpeechDetector()
        speech_detector.run(executor.execute_command_from_text)
    except ValueError as err:
        print('Failed to init Jarvis ears with error', err, 'Aborting...')

if __name__ == '__main__':
    init_jarvis()