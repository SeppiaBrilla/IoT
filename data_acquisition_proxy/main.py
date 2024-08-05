from flask import Flask, request, jsonify, abort
import paho.mqtt.client as mqtt
import json
import asyncio
import threading
from aiocoap import resource, CONTENT, Context, Message
from manager import SensorDataManager
from data import LuminositySensorData, Plant, Position, SensorConfiguration, TemperatureSensorData
from exceptions import AlreadyPresentException, InconsistentPositionException, NotFoundException

manager = SensorDataManager()
app = Flask(__name__)

# MQTT settings
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPICS = [
    ("submit_light_data", 0),
    ("submit_temperature_data", 0),
    ("new_sensor", 0),
    ("update_sensor_position", 0),
    ("delete_sensor", 0),
    ("new_position", 0),
    ("update_position_data", 0),
    ("delete_position", 0),
    ("new_plant", 0),
    ("update_plant", 0),
    ("delete_plant", 0)
]

# MQTT message handling functions
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        for topic, qos in MQTT_TOPICS:
            client.subscribe(topic)
    else:
        print(f"Failed to connect to MQTT broker, return code {rc}")

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    data = json.loads(payload)
    
    if msg.topic == "submit_light_data":
        submit_light_data_handler(data)
    elif msg.topic == "submit_temperature_data":
        submit_temperature_data_handler(data)
    elif msg.topic == "new_sensor":
        new_sensor_handler(data)
    elif msg.topic == "update_sensor_position":
        update_sensor_position_handler(data)
    elif msg.topic == "delete_sensor":
        delete_sensor_handler(data)
    elif msg.topic == "new_position":
        new_position_handler(data)
    elif msg.topic == "update_position_data":
        update_position_data_handler(data)
    elif msg.topic == "delete_position":
        delete_position_handler(data)
    elif msg.topic == "new_plant":
        new_plant_handler(data)
    elif msg.topic == "update_plant":
        update_plant_handler(data)
    elif msg.topic == "delete_plant":
        delete_plant_handler(data)

# Common request handlers for both HTTP, MQTT, and CoAP
def submit_light_data_handler(data):
    if not isinstance(data, dict) or not all(k in data for k in ["ID", "POSITION", "LUMINOSITY", "TIME"]):
        abort(400)

    luminosity_data = LuminositySensorData(
        id=data["ID"],
        position=data["POSITION"],
        luminosity=data["LUMINOSITY"],
        time_stamp=data["TIME"]
    )

    try:
        manager.add_light_data(luminosity_data)
    except (InconsistentPositionException, NotFoundException) as e:
        abort(400, description=str(e))
    
    return jsonify({"status": "success"})

# Common request handlers for both HTTP, MQTT, and CoAP
def submit_temperature_data_handler(data):
    if not isinstance(data, dict) or not all(k in data for k in ["ID", "POSITION", "TEMPERATURE", "TIME"]):
        abort(400)

    luminosity_data = TemperatureSensorData(
        id=data["ID"],
        position=data["POSITION"],
        temperature=data["TEMPERATURE"],
        time_stamp=data["TIME"]
    )

    try:
        manager.add_temperature_data(luminosity_data)
    except (InconsistentPositionException, NotFoundException) as e:
        abort(400, description=str(e))
    
    return jsonify({"status": "success"})


def new_sensor_handler(data):
    if not isinstance(data, dict) or not all(k in data for k in ["ID", "POSITION", "IP"]):
        return "ID, POSITION, and IP fields needed", 400

    try:
        manager.new_sensor(SensorConfiguration(
            id=data["ID"],
            position=data["POSITION"],
            ip=data["IP"]
        ))
    except (AlreadyPresentException, NotFoundException) as e:
        return str(e), 400
    
    return jsonify({"status": "success"})

def update_sensor_position_handler(data):
    if not isinstance(data, dict) or not all(k in data for k in ["ID", "POSITION"]):
        return "ID and POSITION fields needed", 400

    try:
        manager.update_position(sensor_id=data["ID"], new_position=data["POSITION"])
    except NotFoundException as e:
        return str(e), 400
    
    return jsonify({"status": "success"})

def delete_sensor_handler(data):
    if not isinstance(data, dict) or "ID" not in data:
        return "ID field needed", 400

    manager.delete_sensor(sensor_id=data["ID"])

    return jsonify({"status": "success"})

def new_position_handler(data):
    if not isinstance(data, dict) or not all(k in data for k in ["ID", "NAME", "DESCRIPTION"]):
        return "ID, NAME, and DESCRIPTION fields needed", 400

    try:
        manager.new_position(Position(
            id=data["ID"],
            name=data["NAME"],
            description=data["DESCRIPTION"]
        ))
    except AlreadyPresentException as e:
        return str(e), 400

    return jsonify({"status": "success"})

def update_position_data_handler(data):
    if not isinstance(data, dict) or not all(k in data for k in ["ID", "NAME", "DESCRIPTION"]):
        return "ID, NAME, and DESCRIPTION fields needed", 400

    try:
        manager.update_position_data(data["ID"], Position(
            id=data["ID"],
            name=data["NAME"],
            description=data["DESCRIPTION"]
        ))
    except NotFoundException as e:
        return str(e), 400

    return jsonify({"status": "success"})

def delete_position_handler(data):
    if not isinstance(data, dict) or "ID" not in data:
        return "ID field needed", 400

    manager.delete_position(data["ID"])

    return jsonify({"status": "success"})

def new_plant_handler(data):
    if not isinstance(data, dict) or not all(k in data for k in ["ID", "NAME", "DESCRIPTION", "SENSOR", "TYPE"]):
        return "ID, NAME, DESCRIPTION, SENSOR, and TYPE fields needed", 400

    try:
        manager.new_plant(Plant(
            id=data["ID"],
            name=data["NAME"],
            description=data["DESCRIPTION"],
            type=data["TYPE"],
            sensor=data["SENSOR"]
        ))
    except AlreadyPresentException as e:
        return str(e), 400

    return jsonify({"status": "success"})

def update_plant_handler(data):
    if not isinstance(data, dict) or not all(k in data for k in ["ID", "NAME", "DESCRIPTION", "SENSOR", "TYPE"]):
        return "ID, NAME, DESCRIPTION, SENSOR, and TYPE fields needed", 400

    try:
        manager.update_plant(data["ID"], Plant(
            id=data["ID"],
            name=data["NAME"],
            description=data["DESCRIPTION"],
            type=data["TYPE"],
            sensor=data["SENSOR"]
        ))
    except NotFoundException as e:
        return str(e), 400

    return jsonify({"status": "success"})

def delete_plant_handler(data):
    if not isinstance(data, dict) or "ID" not in data:
        return "ID field needed", 400

    manager.delete_plant(data["ID"])

    return jsonify({"status": "success"})

# HTTP Routes
@app.route('/submitLight', methods=['PUT'])
def submit_light_data():
    return submit_light_data_handler(request.json)

@app.route('/submitTemperature', methods=['PUT'])
def submit_temperature_data():
    return submit_temperature_data_handler(request.json)

@app.route('/newSensor', methods=['POST'])
def new_sensor():
    return new_sensor_handler(request.json)

@app.route('/updateSensorPosition', methods=['PATCH'])
def update_sensor_position():
    return update_sensor_position_handler(request.json)

@app.route('/deleteSensor', methods=['DELETE'])
def delete_sensor():
    return delete_sensor_handler(request.json)

@app.route('/newPosition', methods=['POST'])
def new_position():
    return new_position_handler(request.json)

@app.route('/updatePositionData', methods=['PATCH'])
def update_position_data():
    return update_position_data_handler(request.json)

@app.route('/deletePosition', methods=['DELETE'])
def delete_position():
    return delete_position_handler(request.json)

@app.route('/newPlant', methods=['POST'])
def new_plant():
    return new_plant_handler(request.json)

@app.route('/updatePlant', methods=['PATCH'])
def update_plant():
    return update_plant_handler(request.json)

@app.route('/deletePlant', methods=['DELETE'])
def delete_plant():
    return delete_plant_handler(request.json)

# CoAP resource handlers
class CoAPResource(resource.Resource):
    async def render_put(self, request):
        payload = request.payload.decode('utf-8')
        data = json.loads(payload)
        if request.opt.uri_path[0] == 'lightData':
            response = submit_light_data_handler(data)
        elif request.opt.uri_path[0] == 'temperatureData':
            response = submit_temperature_data_handler(data)
        else:
            print(f"request {request.opt.uri_path[0]} unrecognized")
            exit(1)

        return Message(code=CONTENT, payload=json.dumps(response.json).encode('utf-8'))

    async def render_post(self, request):
        payload = request.payload.decode('utf-8')
        data = json.loads(payload)
        if request.opt.uri_path[0] == 'newSensor':
            response = new_sensor_handler(data)
        elif request.opt.uri_path[0] == 'newPosition':
            response = new_position_handler(data)
        elif request.opt.uri_path[0] == 'newPlant':
            response = new_plant_handler(data)
        else:
            print(f"request {request.opt.uri_path[0]} unrecognized")
            exit(1)
        assert not isinstance(response, tuple), f"got error: {response[0]}"
        return Message(code=CONTENT, payload=json.dumps(response.json).encode('utf-8'))

    async def render_patch(self, request):
        payload = request.payload.decode('utf-8')
        data = json.loads(payload)
        if request.opt.uri_path[0] == 'updateSensorPosition':
            response = update_sensor_position_handler(data)
        elif request.opt.uri_path[0] == 'updatePositionData':
            response = update_position_data_handler(data)
        elif request.opt.uri_path[0] == 'updatePlant':
            response = update_plant_handler(data)
        else:
            print(f"request {request.opt.uri_path[0]} unrecognized")
            exit(1)
        assert not isinstance(response, tuple), f"got error: {response[0]}"
        return Message(code=CONTENT, payload=json.dumps(response.json).encode('utf-8'))

    async def render_delete(self, request):
        payload = request.payload.decode('utf-8')
        data = json.loads(payload)
        if request.opt.uri_path[0] == 'deleteSensor':
            response = delete_sensor_handler(data)
        elif request.opt.uri_path[0] == 'deletePosition':
            response = delete_position_handler(data)
        elif request.opt.uri_path[0] == 'deletePlant':
            response = delete_plant_handler(data)
        else:
            print(f"request {request.opt.uri_path[0]} unrecognized")
            exit(1)
        assert not isinstance(response, tuple), f"got error: {response[0]}"
        return Message(code=CONTENT, payload=json.dumps(response.json).encode('utf-8'))

# Function to start the CoAP server
async def start_coap_server():
    root = resource.Site()
    root.add_resource(['lightData'], CoAPResource())
    root.add_resource(['temperatureData'], CoAPResource())
    root.add_resource(['newSensor'], CoAPResource())
    root.add_resource(['updateSensorPosition'], CoAPResource())
    root.add_resource(['deleteSensor'], CoAPResource())
    root.add_resource(['newPosition'], CoAPResource())
    root.add_resource(['updatePositionData'], CoAPResource())
    root.add_resource(['deletePosition'], CoAPResource())
    root.add_resource(['newPlant'], CoAPResource())
    root.add_resource(['updatePlant'], CoAPResource())
    root.add_resource(['deletePlant'], CoAPResource())

    await Context.create_server_context(root)

if __name__ == '__main__':
    # Initialize MQTT client
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    except Exception as e:
        print(f"Failed to connect to MQTT broker: {e}")
        exit(1)
    
    # Start MQTT client in a separate thread
    mqtt_client.loop_start()

    # Start Flask app
    flask_thread = threading.Thread(target=lambda: app.run(host='localhost', port=5000))
    flask_thread.start()

    # Start CoAP server
    asyncio.run(start_coap_server())

