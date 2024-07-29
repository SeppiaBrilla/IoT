from data import LuminositySensorData
from db import Dummy_DB
from exceptions import NoSensorFoundException, InconsistentPositionException

class SensorDataManager:
    def __init__(self) -> None:
        self.db = Dummy_DB()

    def add_data(self, data:LuminositySensorData):

        def query(datapoint:dict):
            return datapoint["id"] == data.id

        sensor = self.db.query("sensors", query)
        if len(sensor) == 1:
            raise NoSensorFoundException(f"Sensor {data.id} not found in db")

        sensor = sensor[0]
        if sensor["position"] != data.position:
            raise InconsistentPositionException(f"Sensor {data.id} is registered at position {sensor['position']}. Got position {data.position}")

        self.db.insert("readings", data.to_dict())
