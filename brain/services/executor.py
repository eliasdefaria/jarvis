import os
import asyncio
from typing import Deque, Callable
from collections import deque
from models.appliances import Appliance
from models.status import Status
from services.kasa_devices import update_lights_status

class Executor:
    running: bool = False
    queue: Deque[Callable] = deque()

    def execute_command_from_text(self, text: str) -> None:
        """
        Translates a text from speech detection or other service into a command Jarvis can execute
        on the house
        """
        
        # TODO: Recognize jarvis input specifically
        # jarvis_triggers = ['jarvis', 'driver', 'garbage', 'drive', 'travis']
        # if not any(trigger in text for trigger in jarvis_triggers):
        #     if os.environ['ENV'] == 'development':
        #         print(f'Speech was not intended for Jarvis... Skipping text "{text}"')
        #     return
        
        light_triggers = ['lights', 'light', 'lighting', 'lamp']
        on_triggers = ['on', 'give me']
        off_triggers = ['off', 'take out']

        rooms = {
            'dining': [Appliance.DINING_ROOM_LIGHT.value],
            'kitchen': [Appliance.KITCHEN_LIGHT.value],
            'living': [Appliance.LARGE_FLOOR_LAMP_1.value, Appliance.LARGE_FLOOR_LAMP_2.value, Appliance.LARGE_FLOOR_LAMP_3.value, Appliance.COUCH_LAMP.value],
            'bathroom': [Appliance.BATHROOM_LIGHT.value],
            'bedroom': [Appliance.BEDROOM_LIGHT.value, Appliance.BEDSIDE_LAMP.value],
            'all': ['all']
        }

        default_lighting = [
            Appliance.DINING_ROOM_LIGHT.value, 
            Appliance.KITCHEN_LIGHT.value, 
            Appliance.LARGE_FLOOR_LAMP_1.value, 
            Appliance.LARGE_FLOOR_LAMP_2.value, 
            Appliance.LARGE_FLOOR_LAMP_3.value, 
            Appliance.COUCH_LAMP.value
        ]

        vibes = {
            'hanging': default_lighting,
            'entertainment': [Appliance.COUCH_LAMP.value],
            'bedtime': [Appliance.BEDSIDE_LAMP.value]
        }
        if any(trigger in text for trigger in light_triggers):
            action = None
            if any(on_trigger in text for on_trigger in on_triggers):
                action = Status.ON.value
            elif any(off_trigger in text for off_trigger in off_triggers):
                action = Status.OFF.value

            lights_to_interact_with = []
            for room_trigger in rooms.keys():
                if room_trigger in text:
                    lights_to_interact_with.extend(rooms[room_trigger])
            
            for vibe in vibes.keys():
                if vibe in text:
                    self.queue.append(lambda: update_lights_status(Status.OFF.value, [], True))
                    lights_to_interact_with.extend(vibes[vibe])
            
            interact_with_all = 'all' in text

            if len(lights_to_interact_with) == 0 and not interact_with_all:
                lights_to_interact_with.extend(default_lighting)
            
            print(f'Turning {lights_to_interact_with} {action}')
            self.queue.append(lambda: update_lights_status(action, lights_to_interact_with, interact_with_all))

        if len(self.queue) == 0:
            print(f'Command did not trigger any actions: {text}')
        elif not self.running:
            self.exec()

    def execute_command_from_fn(self, fn: Callable) -> None:
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
        if len(self.queue) == 0:
            return
            
        self.running = True
        command = self.queue.popleft()
        asyncio.run(command())

        if len(self.queue) > 0:
            self.exec()
        else:
            self.running = False
        