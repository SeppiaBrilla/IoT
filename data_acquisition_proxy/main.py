import json
import asyncio
import os
import threading
from coap_server import start_coap_server
from http_server import app
from mqtt_server import create_mqtt_server

if __name__ == '__main__':
    # Initialize MQTT client
    # create_mqtt_server()
    host_address = os.environ.get("SERVER_ADDRESS")
    host_port = os.environ.get("SERVER_PORT")
    if host_address is None:
        host_address = "localhost"
    if host_port is None:
        host_port = 5000
    flask_thread = threading.Thread(target=lambda: app.run(host=host_address, port=int(host_port)))
    flask_thread.start()

    asyncio.run(start_coap_server())

