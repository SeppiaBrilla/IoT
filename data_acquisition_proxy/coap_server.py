import json
import asyncio
from aiocoap import resource, CONTENT, Context, Message
from manager import SensorDataManager
from data import LuminositySensorData, Plant, Position, SensorConfiguration, TemperatureSensorData
from exceptions import AlreadyPresentException, InconsistentPositionException, NotFoundException

manager = SensorDataManager()

class Light_data(resource.Resource):
    async def render_put(self, request):
        payload = request.payload.decode('utf-8')
        data = json.loads(payload)

        if not isinstance(data, dict) or not all(k in data for k in ["ID", "POSITION", "LUMINOSITY", "TIME"]):
            return Message(code=CONTENT, payload=json.dumps({"status":"failure", "msg":"missing input parameter"}).encode('utf-8'))

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
        
        return Message(code=CONTENT, payload=json.dumps({"status": "success"}).encode('utf-8'))

class Temperature_data(resource.Resource):
    async def render_put(self, request):
        payload = request.payload.decode('utf-8')
        data = json.loads(payload)

        if not isinstance(data, dict) or not all(k in data for k in ["ID", "POSITION", "TEMPERATURE", "TIME"]):
            return Message(code=CONTENT, payload=json.dumps({"status":"failure", "msg":"missing input parameter"}).encode('utf-8'))

        luminosity_data = TemperatureSensorData(
            id=data["ID"],
            position=data["POSITION"],
            temperature=data["TEMPERATURE"],
            time_stamp=data["TIME"]
        )

        try:
            manager.add_temperature_data(luminosity_data)
        except (InconsistentPositionException, NotFoundException) as e:
            return Message(code=CONTENT, payload=json.dumps({"status":"failure", "msg":str(e)}).encode('utf-8'))
        
        return Message(code=CONTENT, payload=json.dumps({"status": "success"}).encode('utf-8'))


class New_sensor(resource.Resource):
    async def render_post(self, request):
        payload = request.payload.decode('utf-8')
        data = json.loads(payload)

        if not isinstance(data, dict) or not all(k in data for k in ["ID", "POSITION", "IP"]):
            return Message(code=CONTENT, payload=json.dumps({"status":"failure", "msg":"missing input parameter"}).encode('utf-8'))

        try:
            manager.new_sensor(SensorConfiguration(
                id=data["ID"],
                position=data["POSITION"],
                ip=data["IP"]
            ))
        except (AlreadyPresentException, NotFoundException) as e:
            return Message(code=CONTENT, payload=json.dumps({"status":"failure", "msg":str(e)}).encode('utf-8'))
        
        return json.dumps({"status": "success"})

class Update_sensor(resource.Resource):
    async def render_patch(self, request):
        payload = request.payload.decode('utf-8')
        data = json.loads(payload)

        if not isinstance(data, dict) or not all(k in data for k in ["ID", "POSITION"]):
            return Message(code=CONTENT, payload=json.dumps({"status":"failure", "msg":"missing input parameter"}).encode('utf-8'))

        try:
            manager.update_position(sensor_id=data["ID"], new_position=data["POSITION"])
        except NotFoundException as e:
            return Message(code=CONTENT, payload=json.dumps({"status":"failure", "msg":str(e)}).encode('utf-8'))

        return Message(code=CONTENT, payload=json.dumps({"status": "success"}).encode('utf-8'))

class Delete_sensor(resource.Resource):
    async def render_delete(self, request):
        payload = request.payload.decode('utf-8')
        data = json.loads(payload)

        if not isinstance(data, dict) or "ID" not in data:
            return Message(code=CONTENT, payload=json.dumps({"status":"failure", "msg":"Missing ID field"}).encode('utf-8'))

        manager.delete_sensor(sensor_id=data["ID"])

        return Message(code=CONTENT, payload=json.dumps({"status": "success"}).encode('utf-8'))

class New_position(resource.Resource):
    async def render_post(self, request):
        payload = request.payload.decode('utf-8')
        data = json.loads(payload)

        if not isinstance(data, dict) or not all(k in data for k in ["ID", "NAME", "DESCRIPTION"]):
            return Message(code=CONTENT, payload=json.dumps({"status":"failure", "msg":"Missing input field"}).encode('utf-8'))

        try:
            manager.new_position(Position(
                id=data["ID"],
                name=data["NAME"],
                description=data["DESCRIPTION"]
            ))
        except AlreadyPresentException as e:
            return Message(code=CONTENT, payload=json.dumps({"status":"failure", "msg":str(e)}).encode('utf-8'))

        return Message(code=CONTENT, payload=json.dumps({"status": "success"}).encode('utf-8'))

class Update_position(resource.Resource):
    async def render_patch(self, request):
        payload = request.payload.decode('utf-8')
        data = json.loads(payload)

        if not isinstance(data, dict) or not all(k in data for k in ["ID", "NAME", "DESCRIPTION"]):
            return Message(code=CONTENT, payload=json.dumps({"status":"failure", "msg":"missing input field"}).encode('utf-8'))

        try:
            manager.update_position_data(data["ID"], Position(
                id=data["ID"],
                name=data["NAME"],
                description=data["DESCRIPTION"]
            ))
        except NotFoundException as e:
            return Message(code=CONTENT, payload=json.dumps({"status":"failure", "msg":str(e)}).encode('utf-8'))

        return json.dumps({"status": "success"})

class Delete_position(resource.Resource):
    async def render_delete(self, request):
        payload = request.payload.decode('utf-8')
        data = json.loads(payload)

        if not isinstance(data, dict) or "ID" not in data:
            return Message(code=CONTENT, payload=json.dumps({"status":"failure", "msg":"missing input parameter"}).encode('utf-8'))

        manager.delete_position(data["ID"])

        return Message(code=CONTENT, payload=json.dumps({"status": "success"}).encode('utf-8'))

class New_plant(resource.Resource):
    async def render_post(self, request):
        payload = request.payload.decode('utf-8')
        data = json.loads(payload)

        if not isinstance(data, dict) or not all(k in data for k in ["ID", "NAME", "DESCRIPTION", "SENSOR", "TYPE"]):
            return Message(code=CONTENT, payload=json.dumps({"status":"failure", "msg":"missing input field"}).encode('utf-8'))

        try:
            manager.new_plant(Plant(
                id=data["ID"],
                name=data["NAME"],
                description=data["DESCRIPTION"],
                type=data["TYPE"],
                sensor=data["SENSOR"]
            ))
        except AlreadyPresentException as e:
            return Message(code=CONTENT, payload=json.dumps({"status":"failure", "msg":str(e)}).encode('utf-8'))

        return Message(code=CONTENT, payload=json.dumps({"status": "success"}).encode('utf-8'))

class Update_plant(resource.Resource):
    async def render_patch(self, request):
        payload = request.payload.decode('utf-8')
        data = json.loads(payload)

        if not isinstance(data, dict) or not all(k in data for k in ["ID", "NAME", "DESCRIPTION", "SENSOR", "TYPE"]):
            return Message(code=CONTENT, payload=json.dumps({"status":"failure", "msg":"missing input field"}).encode('utf-8'))

        try:
            manager.update_plant(data["ID"], Plant(
                id=data["ID"],
                name=data["NAME"],
                description=data["DESCRIPTION"],
                type=data["TYPE"],
                sensor=data["SENSOR"]
            ))
        except NotFoundException as e:
            return Message(code=CONTENT, payload=json.dumps({"status":"failure", "msg":str(e)}).encode('utf-8'))

        return Message(code=CONTENT, payload=json.dumps({"status": "success"}).encode('utf-8'))

class Delete_plant(resource.Resource):
    async def render_delete(self, request):
        payload = request.payload.decode('utf-8')
        data = json.loads(payload)

        if not isinstance(data, dict) or "ID" not in data:
            return Message(code=CONTENT, payload=json.dumps({"status":"failure", "msg":"missing input field"}).encode('utf-8'))

        manager.delete_plant(data["ID"])

        return Message(code=CONTENT, payload=json.dumps({"status": "success"}).encode('utf-8'))

async def start_coap_server():
    root = resource.Site()
    root.add_resource(['lightData'], Light_data())
    root.add_resource(['temperatureData'], Temperature_data())
    root.add_resource(['newSensor'], New_sensor())
    root.add_resource(['updateSensorPosition'], Update_sensor())
    root.add_resource(['deleteSensor'], Delete_sensor())
    root.add_resource(['newPosition'], New_position())
    root.add_resource(['updatePositionData'], Update_position())
    root.add_resource(['deletePosition'], Delete_position())
    root.add_resource(['newPlant'], New_plant())
    root.add_resource(['updatePlant'], Update_plant())
    root.add_resource(['deletePlant'], Delete_plant())
    await Context.create_server_context(root)
    await asyncio.get_running_loop().create_future()
