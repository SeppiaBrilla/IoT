import json
import asyncio
import threading
from coap_server import start_coap_server
from http_server import app
from mqtt_server import create_mqtt_server

if __name__ == '__main__':
    # Initialize MQTT client
    # create_mqtt_server()
    flask_thread = threading.Thread(target=lambda: app.run(host='localhost', port=5000))
    flask_thread.start()

    asyncio.run(start_coap_server())

