import json
import paho.mqtt.client as mqtt
from manager import SensorDataManager
from data import LuminositySensorData, Plant, Position, SensorConfiguration, TemperatureSensorData
from exceptions import AlreadyPresentException, InconsistentPositionException, NotFoundException

manager = SensorDataManager()

def submit_light_data_handler(data):
    if not isinstance(data, dict) or not all(k in data for k in ["ID", "POSITION", "LUMINOSITY", "TIME"]):
        return json.dumps({"status":"failure", "msg":"missing input parameter"})

    luminosity_data = LuminositySensorData(
        id=data["ID"],
        position=data["POSITION"],
        luminosity=data["LUMINOSITY"],
        time_stamp=data["TIME"]
    )

    try:
        manager.add_light_data(luminosity_data)
    except (InconsistentPositionException, NotFoundException) as e:
        return json.dumps({"status":"failure", "msg":str(e)})
    
    return json.dumps({"status": "success"})

def submit_temperature_data_handler(data):
    if not isinstance(data, dict) or not all(k in data for k in ["ID", "POSITION", "TEMPERATURE", "TIME"]):
        return json.dumps({"status":"failure", "msg":"missing input parameter"})

    luminosity_data = TemperatureSensorData(
        id=data["ID"],
        position=data["POSITION"],
        temperature=data["TEMPERATURE"],
        time_stamp=data["TIME"]
    )

    try:
        manager.add_temperature_data(luminosity_data)
    except (InconsistentPositionException, NotFoundException) as e:
        return json.dumps({"status":"failure", "msg":str(e)})
    
    return json.dumps({"status": "success"})

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
        return json.dumps({"status":"failure", "msg":str(e)})
    
    return json.dumps({"status": "success"})

def update_sensor_position_handler(data):
    if not isinstance(data, dict) or not all(k in data for k in ["ID", "POSITION"]):
        return "ID and POSITION fields needed", 400

    try:
        manager.update_position(sensor_id=data["ID"], new_position=data["POSITION"])
    except NotFoundException as e:
        return json.dumps({"status":"failure", "msg":str(e)})    

    return json.dumps({"status": "success"})

def delete_sensor_handler(data):
    if not isinstance(data, dict) or "ID" not in data:
        return json.dumps({"status":"failure", "msg":"Missing ID field"})    

    manager.delete_sensor(sensor_id=data["ID"])

    return json.dumps({"status": "success"})

def new_position_handler(data):
    if not isinstance(data, dict) or not all(k in data for k in ["ID", "NAME", "DESCRIPTION"]):
        return json.dumps({"status":"failure", "msg":"Missing input field"})    

    try:
        manager.new_position(Position(
            id=data["ID"],
            name=data["NAME"],
            description=data["DESCRIPTION"]
        ))
    except AlreadyPresentException as e:
        return json.dumps({"status":"failure", "msg":str(e)})    

    return json.dumps({"status": "success"})

def update_position_data_handler(data):
    if not isinstance(data, dict) or not all(k in data for k in ["ID", "NAME", "DESCRIPTION"]):
        return json.dumps({"status":"failure", "msg":"missing input field"})    

    try:
        manager.update_position_data(data["ID"], Position(
            id=data["ID"],
            name=data["NAME"],
            description=data["DESCRIPTION"]
        ))
    except NotFoundException as e:
        return json.dumps({"status":"failure", "msg":str(e)})    

    return json.dumps({"status": "success"})

def delete_position_handler(data):
    if not isinstance(data, dict) or "ID" not in data:
        return "ID field needed", 400

    manager.delete_position(data["ID"])

    return json.dumps({"status": "success"})

def new_plant_handler(data):
    if not isinstance(data, dict) or not all(k in data for k in ["ID", "NAME", "DESCRIPTION", "SENSOR", "TYPE"]):
        return json.dumps({"status":"failure", "msg":"missing input field"})    

    try:
        manager.new_plant(Plant(
            id=data["ID"],
            name=data["NAME"],
            description=data["DESCRIPTION"],
            type=data["TYPE"],
            sensor=data["SENSOR"]
        ))
    except AlreadyPresentException as e:
        return json.dumps({"status":"failure", "msg":str(e)})    

    return json.dumps({"status": "success"})

def update_plant_handler(data):
    if not isinstance(data, dict) or not all(k in data for k in ["ID", "NAME", "DESCRIPTION", "SENSOR", "TYPE"]):
        return json.dumps({"status":"failure", "msg":"missing input field"})    

    try:
        manager.update_plant(data["ID"], Plant(
            id=data["ID"],
            name=data["NAME"],
            description=data["DESCRIPTION"],
            type=data["TYPE"],
            sensor=data["SENSOR"]
        ))
    except NotFoundException as e:
        return json.dumps({"status":"failure", "msg":str(e)})    

    return json.dumps({"status": "success"})

def delete_plant_handler(data):
    if not isinstance(data, dict) or "ID" not in data:
        return json.dumps({"status":"failure", "msg":"missing input field"})    

    manager.delete_plant(data["ID"])

    return json.dumps({"status": "success"})


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

def create_mqtt_server():
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    except Exception as e:
        print(f"Failed to connect to MQTT broker: {e}")
        exit(1)
    mqtt_client.loop_start()
