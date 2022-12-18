from multiprocessing.sharedctypes import Value
from peewee import SmallIntegerField
from kasa import SmartStrip, Discover, DeviceType, SmartBulb, SmartDeviceException
from db.db import Plug, Device, Bulb
from models.appliances import Appliance
from models.status import Status
from typing import List, Union
import asyncio

async def init_kasa_devices() -> None:
    print('Inializing connections to kasa devices...')

    try:
        devices = await Discover.discover()
        print('Device Count: ', len(devices.keys()))

        for addr, dev in devices.items():
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
                        status=int(outlet.is_on),
                        device=device,
                        kasa_device_id=outlet.device_id
                    )
            elif device.type == DeviceType.Bulb.value:
                bulb = SmartBulb(device.ip)
                await bulb.update()
                Bulb.create(
                    name=bulb.alias,
                    status=int(bulb.is_on),
                    device=device,
                    kasa_device_id=bulb.device_id
                )
    except SmartDeviceException as err:
        raise ValueError(err)

async def update_all_devices() -> None:
    await asyncio.gather(*[update_device_status(device) for device in Device.select()])

async def update_device_status(device: Device) -> None:
    try:
        if device.type == DeviceType.Strip.value:
            strip = SmartStrip(str(device.ip))
            await strip.update()

            for outlet in strip.children:
                update = Plug.update({ Plug.status: int(outlet.is_on) }).where(Plug.kasa_device_id == outlet.device_id)
                update.execute()
        elif device.type == DeviceType.Bulb.value:
            bulb = SmartBulb(str(device.ip))
            await bulb.update()
            update = Bulb.update({ Bulb.status: int(bulb.is_on) }).where(Bulb.kasa_device_id == bulb.device_id)
            update.execute()
    except SmartDeviceException as err:
        print(f'Failed to update device. Skipping update for {device.name}...', err)

async def set_bulb_status(appliance: Bulb, device_metadata: str, status: Status) -> None:
    [ ip, type ] = device_metadata.split('_')

    if int(type) == DeviceType.Bulb.value:
        try:
            bulb = SmartBulb(ip)
            await bulb.update()

            if bulb.alias != appliance.name or (status.value == Status.ON.value and bulb.is_on) or (status.value == Status.OFF.value and bulb.is_off):
                    return
            
            fn = bulb.turn_on if status.value == Status.ON.value else bulb.turn_off

            await fn(transition=1000)
        
            appliance.status = status.value   
            appliance.save()
        except SmartDeviceException as err:
            print(f'Failed to set bulb status. Skipping update for {appliance.name}...', err)
    
async def update_lights_status(status: Status, lights: List[str] = [], all: bool = False) -> None:
    appliances = {}
    for device in Device.select():
        # TODO: Add check for if device is smart strip here
        for bulb in Bulb.select().join(Device).where(Device.id == device.id):
            print('Bulb States: ', bulb.name, 'on' if bulb.status == 1 else 'off')
            if (bulb.name in lights or all):
                device_metadata = f'{device.ip}_{device.type}'
                if device_metadata not in appliances:
                    appliances[device_metadata] = None
                appliances[device_metadata] = bulb
    
    await asyncio.gather(*[set_bulb_status(appliances[device_metadata], device_metadata, status) for device_metadata in appliances.keys()])

if __name__ == '__main__':
    asyncio.run(init_kasa_devices())