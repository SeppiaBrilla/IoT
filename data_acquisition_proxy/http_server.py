from flask import Flask, request, jsonify, abort
from manager import SensorDataManager
from data import LuminositySensorData, Plant, Position, SensorConfiguration, TemperatureSensorData
from exceptions import AlreadyPresentException, InconsistentPositionException, NotFoundException

manager = SensorDataManager()
app = Flask(__name__)

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

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "success"})
