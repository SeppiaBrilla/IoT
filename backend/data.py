class SensorData:
    def __init__(self, id:str, position:str) -> None:
        self.id = id
        self.position = position

class LuminositySensorData(SensorData):
    def __init__(self, id:str, position:str, luminosity:float) -> None:
        self.id = id
        self.position = position
        self.luminosity = luminosity

    def to_dict(self):
        return {
            "id": self.id,
            "position": self.position,
            "luminosity": self.luminosity
        }
