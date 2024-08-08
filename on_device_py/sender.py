import network
import requests
import machine
from time import sleep, time
import asyncio
import json
import microcoapy

def receivedMessageCallback(packet, sender):
        print('Message received:', packet.toString(), ', from: ', sender)
        print('Message payload: ', packet.payload.decode('unicode_escape'))

class Sender:
    def __init__(self, config, readers):
        self.config = config
        self.readers = readers
        self.connect()
        self.sensor = machine.ADC(4)
        self.client = None

    def connect(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(self.config["wifi_ssid"], self.config["wifi_pwd"])
        for i in range(20):
            print(f'({i}) Waiting for connection...')
            sleep(1)
            if wlan.isconnected():
                break
        if not wlan.isconnected():
            print("cannot establish connection")
            return
        wlan_config = wlan.ifconfig()
        wlan_config = (self.config["device_ip"], wlan_config[1], wlan_config[2], wlan_config[3])
        wlan.ifconfig(wlan_config)
        response = requests.get(f'http://{self.config["server_address"]}/ping')
        print(response.status_code)
        
    def collect_and_send(self, loop):
        async def gatherer():
            while True:
                await asyncio.gather(self.__read_temperature(), self.__read_2())
        task = loop.create_task(gatherer())
        return loop
    
    async def __read_temperature(self):
    # Read the raw ADC value
        adc_value = self.sensor.read_u16()

        # Convert ADC value to voltage
        voltage = adc_value * (3.3 / 65535.0)

        # Temperature calculation based on sensor characteristics
        temperature_celsius = 27 - (voltage - 0.706) / 0.001721

        print(f"temperature: {temperature_celsius} C")
        payload = {
            "ID":self.config['device_id'],
            "POSITION":"P01",
            "TEMPERATURE": temperature_celsius,
            "TIME":time()
        }
        if self.config["protocol"] == "HTTP":
            await self.http_request(payload, "submitTemperature")
        elif self.config["protocol"] == "COAP":
            await self.coap_request(payload, "temperatureData")
        else:
            raise Exception(f"Unknown protocol {self.config['protocol']}")
        await asyncio.sleep(self.config["sampling_rate"])
    
    async def http_request(self, payload, parameter):
        try:
            response = requests.put(
                f'http://{self.config["server_address"]}:{self.config["server_port"]}/{parameter}',
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'})
            print(response.text)
        except Exception as e:
            print("Error:", e)
            
    async def coap_request(self, payload, parameter):
        if self.client is None:
            self.client = microcoapy.Coap()
            self.client.responseCallback = receivedMessageCallback
        self.client.start()
        bytesTransferred = self.client.put(
            self.config["server_address"],
            self.config["server_port"],
            parameter,
            json.dumps(payload),
            None,
            microcoapy.COAP_CONTENT_FORMAT.COAP_TEXT_PLAIN
        )
        print("[PUT] Sent bytes: ", bytesTransferred)

        self.client.poll(2000)

        self.client.stop()

    async def __read_2(self):
        print(f"sending {42} to 2")
        await asyncio.sleep(self.config["sampling_rate"])
