from kasa import SmartStrip, Discover, DeviceType
from db.db import Plug, Device 
from models.appliances import Appliance
from models.status import Status
from typing import List
import asyncio

async def init_kasa_devices():
    print('Inializing connections to kasa devices...')
    devices = await Discover.discover()
    print('have devices', devices)
    for addr, dev in devices.items():
        print('got address', addr, dev)
        await dev.update()
        device = Device.create(
            kasa_device_id=dev.device_id,
            name=dev.alias,
            ip=addr,
            type=dev.device_type.value
        )

        # TODO: Add support for all device types
        if device.type == DeviceType.Strip.value:
            strip = SmartStrip(device.ip)
            await strip.update()
            for outlet in strip.children:
                Plug.create(
                    name=outlet.alias,
                    status=(1 if outlet.is_on else 0),
                    device=device,
                    kasa_device_id=outlet.device_id
                )

async def lights_on(lights: List[Appliance] = [], all = False) -> None:
    appliances = {}
    for device in Device.select():
        # TODO: Remove check below once other kasa devices are integrated
        # if 'plugs' not in device:
        #     continue
        for plug in Plug.select().join(Device).where(Device.id == device.id):
            print(all, plug.status, )
            if (plug.name in lights or all) and plug.status == Status.OFF.value:
                device_metadata = f'{device.ip}_{device.type}'
                if device_metadata not in appliances:
                    appliances[device_metadata] = []
                appliances[device_metadata].append(plug)
    print(appliances)
    for device_metadata in appliances.keys():
        [ ip, type ] = device_metadata.split('_')

        # TODO: Add support for all device types
        if int(type) == DeviceType.Strip.value:
            strip = SmartStrip(ip)
            await strip.update()
            
            for outlet in strip.children:
                if outlet.is_on:
                    continue
                for appliance in appliances[device_metadata]:
                    if outlet.alias == appliance.name:
                        await outlet.turn_on()
                        appliance.status = Status.ON.value                


    return
                
    

if __name__ == '__main__':
    asyncio.run(init_kasa_devices())