from data import LuminositySensorData, Plant, SensorConfiguration, Position, TemperatureSensorData
from exceptions import NotFoundException, InconsistentPositionException, AlreadyPresentException
from db import DB

class SensorDataManager:
    def __init__(self) -> None:
        self.db = DB()

    def add_light_data(self, data:LuminositySensorData):


        sensor = self.db.get_device(data.id)
        if len(sensor) == 0:
            raise NotFoundException(f"Sensor {data.id} not found in db")

        sensor = sensor[0]
        if sensor["position"] != data.position:
            raise InconsistentPositionException(f"Sensor {data.id} is registered at position {sensor['position']}. Got position {data.position}")

        self.db.insert_time_series(measurement="Light_data", tags={
                                   "device": data.id,
                                   "position": data.position}, 
                                   values={"light":str(data.luminosity)},
                                   time= data.time_stamp)

    def add_temperature_data(self, data:TemperatureSensorData):


        sensor = self.db.get_device(data.id)
        if len(sensor) == 0:
            raise NotFoundException(f"Sensor {data.id} not found in db")

        sensor = sensor[0]
        if sensor["position"] != data.position:
            raise InconsistentPositionException(f"Sensor {data.id} is registered at position {sensor['position']}. Got position {data.position}")

        self.db.insert_time_series(measurement="Temperature_data", tags={
                                   "device": data.id,
                                   "position": data.position}, 
                                   values={"temperature":str(data.temperature)},
                                   time= data.time_stamp)


    def new_sensor(self, device:SensorConfiguration):
        
        if len(self.db.get_device(device.id)) > 0:
            raise AlreadyPresentException(f"device {device.id} already present in db")

        if len(self.db.get_position(device.position)) == 0:
            raise NotFoundException(f"position {device.position} not found")

        self.db.create_device(device)

    def update_position(self, sensor_id:str, new_position:str):

        sensor = self.db.get_device(sensor_id)
        if len(sensor) == 0:
            raise NotFoundException(f"Sensor {sensor_id} not found in db")

        if len(self.db.get_position(new_position)) == 0:
            raise NotFoundException(f"position {new_position} not found")

        sensor = sensor[0] 
        sensor = SensorConfiguration(id=sensor_id, position=new_position, ip=sensor["ip"])

        self.db.update_device(sensor)

    def delete_sensor(self, sensor_id:str):
        self.db.delete_device(sensor_id)

    def new_position(self, position:Position):

        if len(self.db.get_position(position.id)) > 0:
            raise AlreadyPresentException(f"device {position.id} already present in db")

        self.db.create_position(position)

    def update_position_data(self, position_id:str, new_position_data:Position):

        position = self.db.get_position(position_id)
        if len(position) == 0:
            raise NotFoundException(f"Position {position_id} not found in db")

        self.db.update_position(new_position_data)

    def delete_position(self, position_id:str):
        self.db.delete_position(position_id)

    def new_plant(self, plant:Plant):

        if len(self.db.get_plant(plant.id)) > 0:
            raise AlreadyPresentException(f"Plant {plant.id} already present in db")

        self.db.create_plant(plant)

    def update_plant(self, plant_id:str, new_plant_data:Plant):

        position = self.db.get_plant(plant_id)
        if len(position) == 0:
            raise NotFoundException(f"Plant {plant_id} not found in db")

        self.db.update_plant(new_plant_data)

    def delete_plant(self, plant_id:str):
        self.db.delete_plant(plant_id)
