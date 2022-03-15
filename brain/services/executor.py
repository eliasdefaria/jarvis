from typing import Deque
from collections import deque
import asyncio

class Executor:
    running: bool = False
    queue: Deque[function] = deque()

    def execute_command_from_text(self, text: str) -> None:
        """
        Translates a text from speech detection or other service into a command Jarvis can execute
        on the house
        """
        if 'lights' in text or 'light' in text:
            print('lights moving!')
            # Append lights command based on logic to queue
        
        if not self.running:
            self.exec()

    def execute_command_from_fn(self, fn: function) -> None:
        """
        Checks to ensure function passed in can be run currently or slots it into command queue if not
        """
        self.queue.append(fn)
        if not self.running:
            self.exec()
    
    def exec(self) -> None:
        """
        Recursively takes the first command in the command queue and executes it
        """
        self.running = True
        command = self.queue.popLeft()
        asyncio.run(command)

        if len(self.queue) > 0:
            exec()
        else:
            self.running = False
        