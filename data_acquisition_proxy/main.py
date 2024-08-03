from flask import Flask, request, jsonify, abort
import paho.mqtt.client as mqtt
from manager import SensorDataManager
from data import LuminositySensorData, Plant, Position, SensorConfiguration
from exceptions import AlreadyPresentException, InconsistentPositionException, NotFoundException

manager = SensorDataManager()
app = Flask(__name__)

@app.route('/submit', methods=['PUT'])
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
    if not "TIME" in data:
        return abort(400)

    luminosity_data = LuminositySensorData(id=data["ID"],
                                           position=data["POSITION"],
                                           luminosity=data["LUMINOSITY"],
                                           time_stamp=data["TIME"])

    try:
        manager.add_data(luminosity_data)
    except InconsistentPositionException as e:
        return abort(400), str(e)
    except NotFoundException as e:
        return abort(400), str(e)

    return jsonify({"status": "success"})

@app.route('/newSensor', methods=['POST'])
def new_sensor():
    data = request.json
    if not isinstance(data, dict):
        return "Not a json body", 400
    if not "ID" in data:
        return "ID field needed", 400
    if not "POSITION" in data:
        return "POSITION field needed", 400
    if not "IP" in data:
        return "IP field needed", 400

    try:
        manager.new_sensor(SensorConfiguration(id=data["ID"],
                                           position=data["POSITION"],
                                           ip=data["IP"]))
    except AlreadyPresentException as e:
        return str(e), 400
    except NotFoundException as e:
        return str(e), 400
    return jsonify({"status": "success"})

@app.route('/updateSensorPosition', methods=['PATCH'])
def update_sensor_position():
    data = request.json
    if not isinstance(data, dict):
        return "Not a json body", 400
    if not "ID" in data:
        return "ID field needed", 400
    if not "POSITION" in data:
        return "POSITION field needed", 400

    try:
        manager.update_position(sensor_id=data["ID"],
                       new_position=data["POSITION"])
    except NotFoundException as e:
        return str(e), 400

    return jsonify({"status": "success"})

@app.route('/deleteSensor', methods=['DELETE'])
def delete_sensor():
    data = request.json
    if not isinstance(data, dict):
        return "Not a json body", 400
    if not "ID" in data:
        return "ID field needed", 400

    manager.delete_sensor(sensor_id=data["ID"])

    return jsonify({"status": "success"})

@app.route('/newPosition', methods=["POST"])
def new_position():
    data = request.json
    if not isinstance(data, dict):
        return "Not a json body", 400
    if not "ID" in data:
        return "ID field needed", 400
    if not "NAME" in data:
        return "NAME field needed", 400
    if not "DESCRIPTION" in data: 
        return "DESCRIPTION field needed", 400
    
    try:
        manager.new_position(Position(id=data["ID"], name=data["NAME"], description=data["DESCRIPTION"]))
    except AlreadyPresentException as e:
        return str(e), 400

    return jsonify({"status": "success"})

@app.route('/updatePositionData', methods=["PATCH"])
def update_position_data():
    data = request.json
    if not isinstance(data, dict):
        return "Not a json body", 400
    if not "ID" in data:
        return "ID field needed", 400
    if not "NAME" in data:
        return "NAME field needed", 400
    if not "DESCRIPTION" in data: 
        return "DESCRIPTION field needed", 400

    try:
        manager.update_position_data(data["ID"], Position(id=data["ID"], name=data["NAME"], description=data["DESCRIPTION"]))
    except NotFoundException as e:
        return str(e), 400

    return jsonify({"status": "success"})

@app.route('/deletePosition', methods=["DELETE"])
def delete_position():
    data = request.json
    if not isinstance(data, dict):
        return "Not a json body", 400
    if not "ID" in data:
        return "ID field needed", 400

    manager.delete_position(data["ID"])

    return jsonify({"status": "success"})

@app.route('/newPlant', methods=["POST"])
def new_plant():
    data = request.json
    if not isinstance(data, dict):
        return "Not a json body", 400
    if not "ID" in data:
        return "ID field needed", 400
    if not "NAME" in data:
        return "NAME field needed", 400
    if not "DESCRIPTION" in data: 
        return "DESCRIPTION field needed", 400
    if not "SENSOR" in data: 
        return "SENSOR field needed", 400
    if not "TYPE" in data: 
        return "TYPE field needed", 400

    try:
        manager.new_plant(Plant(id=data["ID"], name=data["NAME"], description=data["DESCRIPTION"], type=data["TYPE"], sensor=data["SENSOR"]))
    except AlreadyPresentException as e:
        return str(e), 400

    return jsonify({"status": "success"})

@app.route('/updatePlant', methods=["PATCH"])
def update_plant():
    data = request.json
    if not isinstance(data, dict):
        return "Not a json body", 400
    if not "ID" in data:
        return "ID field needed", 400
    if not "NAME" in data:
        return "NAME field needed", 400
    if not "DESCRIPTION" in data: 
        return "DESCRIPTION field needed", 400
    if not "SENSOR" in data: 
        return "SENSOR field needed", 400
    if not "TYPE" in data: 
        return "TYPE field needed", 400

    try:
        manager.update_plant(data["ID"], Plant(id=data["ID"], name=data["NAME"], description=data["DESCRIPTION"], type=data["TYPE"], sensor=data["SENSOR"]))
    except NotFoundException as e:
        return str(e), 400

    return jsonify({"status": "success"})

@app.route('/deletePlant', methods=["DELETE"])
def delete_plant():
    data = request.json
    if not isinstance(data, dict):
        return "Not a json body", 400
    if not "ID" in data:
        return "ID field needed", 400

    manager.delete_plant(data["ID"])

    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(host='localhost', port=5000)
