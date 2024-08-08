from bluetooth_configuration import BLEConfigReceiver
from sender import Sender
import json
import asyncio

f = open("config.json")
config = json.load(f)
f.close()
temperature_sensor = machine.ADC(4)
sender = Sender(config["configs"][-1], {})
loop = asyncio.get_event_loop()
loop = sender.collect_and_send(loop)
loop.run_forever()
