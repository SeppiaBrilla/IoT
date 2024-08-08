# This example demonstrates a simple temperature sensor peripheral.
#
# The sensor's local value is updated, and it will notify
# any connected central every 10 seconds.

import bluetooth
import random
import struct
import time
import machine
import ubinascii
import json
import network
from utime import sleep
from ble_advertising import advertising_payload
from micropython import const
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")

def file_exists(file):
    try:
        f = open(file)
        f.close()
        return True
    except:
        return False

class BLEConfigReceiver:
    def __init__(self, ble, name="mpy-01"):
        self._ble = ble
        self._ble.active(True)
        self._new_configuration = False
        self._connections = set()
        self._led = machine.Pin("LED", machine.Pin.OUT)
        self._payload = advertising_payload(name=name, services=[_UART_UUID])
        self.init_ble()
        self.data = ""
        self.config_file = "config.json"
        if not file_exists(self.config_file):
            f = open(self.config_file, "w")
            f.write('{"configs":[]}')
            f.close()

    def init_ble(self):
        self._ble.irq(self.ble_irq)
        self.register_services()
        self._advertise()

    def ble_irq(self, event, data):
        if event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            self._led.off()
            print("Closed connection", conn_handle)
            self._connections.remove(conn_handle)
            self.reformat_data()
        elif event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self._led.on()
            print("New connection", conn_handle)
            self._connections.add(conn_handle)
        elif event == _IRQ_GATTS_WRITE: 
            conn_handle, attr_handle = data
            value = self._ble.gatts_read(attr_handle)
            print(f"Received data: {value.decode('utf-8')}")
            self.data += value.decode("utf-8")
            
            
    def register_services(self):
        FILE_SERVICE_UUID = bluetooth.UUID('0000ffe0-0000-1000-8000-00805f9b34fb')
        FILE_CHAR_UUID = bluetooth.UUID('0000ffe1-0000-1000-8000-00805f9b34fb')

        FILE_SERVICE = (FILE_SERVICE_UUID, ((FILE_CHAR_UUID, bluetooth.FLAG_WRITE | bluetooth.FLAG_WRITE_NO_RESPONSE,),))
        SERVICES = (FILE_SERVICE,)

        ((self.handle,),) = self._ble.gatts_register_services(SERVICES)

    def send(self, data):
        for conn_handle in self._connections:
            self._ble.gatts_notify(conn_handle, self._handle_tx, data)

    def _is_connected(self):
        return len(self._connections) > 0

    def _advertise(self, interval_us=500000):
        print("Starting advertising")
        self._ble.gap_advertise(interval_us, adv_data=self._payload)
    
    def reformat_data(self):
        if self.data == "":
            print("data not received")
            return
        data = json.loads(self.data)
        properties = list(data.keys())
        for prop in ["device_ip", "server_address", "protocol", "device_id", "wifi_ssid", "wifi_pwd", "plant", "sampling_rate", "position_id"]:
            if prop not in properties:
                print(f"property {prop} missing, got {properties}")
                return
        f = open(self.config_file)
        current_config = json.load(f)
        f.close()
        self.data = ""
        print(f"got new configuration: {data}")
        if not self.try_connect(data["wifi_ssid"], data["wifi_pwd"]):
            print("wrong wifi credential, retry")
            return
        current_config["configs"].append(data)
        f = open(self.config_file, "w")
        json.dump(current_config, f)
        f.close()
        print("new configuration saved")
        self._new_configuration = True
        
       
    def try_connect(self, ssid, pwd):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(ssid, pwd)
        connected = False
        for i in range(20):
            print(f'({i}) Waiting for connection...')
            sleep(1)
            if wlan.isconnected():
                connected = True
                break
        return connected
    
    def updated_configuration(self):
        if self._new_configuration:
           self._new_configuration = False
           return True
        return False
        
if __name__ == "__main__":
    ble = bluetooth.BLE()
    filer = BLEConfigReceiver(ble)