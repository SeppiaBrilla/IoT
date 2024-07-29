# from influxdb_client import InfluxDBClient
# from influxdb_client.client.write_api import SYNCHRONOUS
#
# token = "8BQPrGsKQxp_bI4yxW1kQ4Xu7xniQa7XsmbVlzzS3zRdAmV7ew6J0ql_dehOaWIXionTOnZOMMI5UJETjW1D7A=="
#
# client = InfluxDBClient(url="http://localhost:8086", token=token, org="ioT")
# write_api = client.write_api(write_options=SYNCHRONOUS)
# write_api.write("IoT", "IoT", ["light,location=room1 light_level=1"])

from flask import Flask, request, jsonify, abort
import paho.mqtt.client as mqtt
from manager import SensorDataManager
from data import LuminositySensorData
from exceptions import InconsistentPositionException, NoSensorFoundException

manager = SensorDataManager()
app = Flask(__name__)

# mqtt_client = mqtt.Client()

@app.route('/submit', methods=['POST'])
def submit_data():
    data = request.json
    if not isinstance(data, dict):
        return abort(400)
    if not "ID" in data:
        return abort(400)
    if not "POSITION" in data:
        return abort(400)
    if not "LUMINOSITY" in data:
        return abort(400)

    luminosity_data = LuminositySensorData(id=data["ID"],
                                           position=data["POSITION"],
                                           luminosity=data["LUMINOSITY"])

    try:
        manager.add_data(luminosity_data)
    except InconsistentPositionException as e:
        return abort(400), str(e)
    except NoSensorFoundException as e:
        return abort(400), str(e)

    return jsonify({"status": "success"})

# def on_message(client, userdata, msg):
    # pass
    # if msg.topic == "sensor/config/sampling_rate":
        # handle sampling rate update
    # elif msg.topic == "sensor/config/change_position":
        # handle position change
    # Implement any necessary updates based on received messages

# mqtt_client.on_message = on_message
# mqtt_client.connect("your_MQTT_BROKER_IP", 1883, 60)
# mqtt_client.subscribe("sensor/config/#")
# mqtt_client.loop_start()

if __name__ == '__main__':
    app.run(host='localhost', port=5000)
