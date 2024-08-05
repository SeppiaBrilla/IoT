import asyncio
from bleak import BleakClient, BleakScanner

async def discover_devices():
    devices = await BleakScanner.discover()
    return devices

async def send_file(address, data, characteristic_uuid):
    client = BleakClient(address)
    try:
        await client.connect()
        print(f"Connected to {address}")
        
        # BLE has a limit on the maximum size of data that can be sent in a single write operation.
        # Usually, it is 20 bytes. Hence, we will chunk the data accordingly.
        CHUNK_SIZE = 20
        data = data.encode('utf-8')
        for i in range(0, len(data), CHUNK_SIZE):
            chunk = data[i:i + CHUNK_SIZE]
            await client.write_gatt_char(characteristic_uuid, chunk)
            print(f"Sent chunk {i // CHUNK_SIZE + 1}")

        print(f"configuration successfully sent to {address}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await client.disconnect()
        print(f"Disconnected from {address}")

if __name__ == "__main__":
    target_name = "mpy-01"
    characteristic_uuid = "0000ffe1-0000-1000-8000-00805f9b34fb"

    print("Scanning for devices...")
    devices = asyncio.run(discover_devices())
    print("select a device:")
    for i, device in enumerate(devices):
        print(f"({i}) {device.name}")
    device_idx = 0
    while 1:
        try: 
            device_idx = int(input(">> "))
            if device_idx >= 0 and device_idx < len(devices):
                break
        except:
            print(f"wrong device id, insert a value between 0 and {len(devices)}")
    target_device = devices[device_idx]
    device_id = input("what is going to be the id of the new device?\n>> ")
    ssid = input("what is going to be the WIFI SSID of the new device?\n>> ")
    pwd = input("what is the WIFI password?\n>> ")
    data = f"{device_id}_SEP_{ssid}_SEP_{pwd}"
    if target_device:
        asyncio.run(send_file(target_device.address, data, characteristic_uuid))
    else:
        print(f"Device named {target_name} not found.")
