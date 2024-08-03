class SensorData:
    def __init__(self, id:str, position:str) -> None:
        self.id = id
        self.position = position

class LuminositySensorData(SensorData):
    def __init__(self, id:str, position:str, luminosity:float, time_stamp:float) -> None:
        self.id = id
        self.position = position
        self.luminosity = luminosity
        self.time_stamp = time_stamp

    def to_dict(self):
        return {
            "id": self.id,
            "position": self.position,
            "luminosity": self.luminosity,
            "time_stamp": self.time_stamp
        }

class SensorConfiguration(SensorData):
    def __init__(self, id:str, position:str, ip:str) -> None:
        super().__init__(id, position)
        self.ip = ip

class Position:
    def __init__(self, id:str, name:str, description:str) -> None:
        self.id = id
        self.name = name
        self.description = description

class Plant:
    def __init__(self, id:str, type:str, name:str="", description:str="", sensor:str=""):
        self.id = id
        self.name = name
        self.description = description
        self.sensor = sensor
        self.type = type
