import influxdb_client, os
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime
from data import Position, SensorConfiguration, Plant

class DB:
    def __init__(self) -> None:
        super().__init__()
        self.token = os.environ.get("INFLUXDB_TOKEN")
        self.org = os.environ.get("INFLUXDB_ORG") 
        self.bucket:str = os.environ.get("INFLUXDB_BUCKET")
        self.url = "https://us-east-1-1.aws.cloud2.influxdata.com"

        assert self.token is not None, "could not find a token. Set it up via the INFLUXDB_TOKEN"
        assert self.org is not None, "could not find a org. Set it up via the INFLUXDB_ORG"
        assert self.bucket is not None, "could not find a bucket. Set it up via the INFLUXDB_BUCKET"

        self.client = influxdb_client.InfluxDBClient(url=self.url, 
                                                           token=self.token, 
                                                           org=self.org)

    def insert_time_series(self, measurement: str, values: dict[str, str], tags:dict[str, str], time:float) -> None:
        
        write_api = self.client.write_api(write_options=SYNCHRONOUS)

        point = Point(measurement)
        for k,v in values.items():
            point.field(k, v)
        for k,v in tags.items():
            point.tag(k,v)

        point.time(datetime.fromtimestamp(time))

        write_api.write(bucket=self.bucket, org=self.org, record=(point))

    def query_time_series(self, measurement:str, time:dict[str, str], values:dict[str,str], tags:dict[str,str], aggregation:str|None = None):
        function = f"""fn(r) => r._measurement == "{measurement}" """

        for k,v in values.items():
            function += f"""and r_{k} == "{v}" """
        for k,v in tags.items():
            function += f"""and r_{k} == "{v}" """

        query = f"""from(bucket: "{self.bucket}")
        |> range(start:{time["start"]}, stop:{time["stop"]})
        |> filter({function})
        """

        if not aggregation is None:
            query += f"\n\t|>{aggregation}"

        query_api = self.client.query_api()
        tables = query_api.query(query, org=self.org)

        return tables

    def create_device(self, sensor_configuration:SensorConfiguration):

        write_api = self.client.write_api(write_options=SYNCHRONOUS)

        point = Point('device') \
            .tag("deviceId", sensor_configuration.id) \
            .field('ip', sensor_configuration.ip) \
            .field('position', sensor_configuration.position)

        client_response = write_api.write(bucket=self.bucket, record=point)

        if not client_response is None:
            raise Exception(client_response)

    def get_device(self, device_id=None) -> list:

        query_api = self.client.query_api()
        device_filter = ''
        if device_id:
            device_id = str(device_id)
            device_filter = f'r.deviceId == "{device_id}"'

        flux_query = f'from(bucket: "{self.bucket}") ' \
                     f'|> range(start: 0) ' \
                     f'|> filter(fn: (r) => r._measurement == "device" and {device_filter}) ' \
                     f'|> last()'
 
        response = query_api.query(flux_query)
        result = []
        for table in response:
            for record in table.records:
                try:
                    _ = 'updatedAt' in record
                except KeyError:
                    record['updatedAt'] = record.get_time()
                    record[record.get_field()] = record.get_value()
                result.append(record.values)
        return result

    def update_device(self, device:SensorConfiguration):
        self.create_device(device)

    def delete_device(self, device_id:str):
        delete_api = self.client.delete_api()
        predicate = f'deviceId == "{device_id}"'
        delete_api.delete(
            start=datetime.fromtimestamp(0),
            stop=datetime.now(),
            bucket=self.bucket,
            org=self.org,
            predicate=predicate)

    def create_position(self, position:Position):

        write_api = self.client.write_api(write_options=SYNCHRONOUS)

        point = Point('position') \
            .tag("positionId", position.id) \
            .field('name', position.name) \
            .field('description', position.description)

        client_response = write_api.write(bucket=self.bucket, record=point)

        if not client_response is None:
            raise Exception(client_response)

    def get_position(self, position_id=None) -> list:

        query_api = self.client.query_api()
        device_filter = ''
        if position_id:
            position_id = str(position_id)
            device_filter = f'r.positionId == "{position_id}"'

        flux_query = f'from(bucket: "{self.bucket}") ' \
                     f'|> range(start: 0) ' \
                     f'|> filter(fn: (r) => r._measurement == "position" and {device_filter}) ' \
                     f'|> last()'
        
        response = query_api.query(flux_query)
        result = []
        for table in response:
            for record in table.records:
                try:
                    _ = 'updatedAt' in record
                except KeyError:
                    record['updatedAt'] = record.get_time()
                    record[record.get_field()] = record.get_value()
                result.append(record.values)
        return result

    def update_position(self, position:Position):
        self.create_position(position)

    def delete_position(self, position_id:str):
        delete_api = self.client.delete_api()
        predicate = f'positionId == "{position_id}"'
        delete_api.delete(
            start=datetime.fromtimestamp(0),
            stop=datetime.now(),
            bucket=self.bucket,
            org=self.org,
            predicate=predicate)

    def create_plant(self, plant:Plant):

        write_api = self.client.write_api(write_options=SYNCHRONOUS)

        point = Point('plant') \
            .tag("plantId", plant.id) \
            .field('name', plant.name) \
            .field('description', plant.description) \
            .field('sensor', plant.sensor) \
            .field('type', plant.type)

        client_response = write_api.write(bucket=self.bucket, record=point)

        if not client_response is None:
            raise Exception(client_response)

    def get_plant(self, plant_id=None) -> list:

        query_api = self.client.query_api()
        device_filter = ''
        if plant_id:
            plant_id = str(plant_id)
            device_filter = f'r.plantId == "{plant_id}"'

        flux_query = f'from(bucket: "{self.bucket}") ' \
                     f'|> range(start: 0) ' \
                     f'|> filter(fn: (r) => r._measurement == "plant" and {device_filter}) ' \
                     f'|> last()'
        
        response = query_api.query(flux_query)
        result = []
        for table in response:
            for record in table.records:
                try:
                    _ = 'updatedAt' in record
                except KeyError:
                    record['updatedAt'] = record.get_time()
                    record[record.get_field()] = record.get_value()
                result.append(record.values)
        return result

    def update_plant(self, plant:Plant):
        self.create_plant(plant)

    def delete_plant(self, plant_id:str):
        delete_api = self.client.delete_api()
        predicate = f'plantId == "{plant_id}"'
        delete_api.delete(
            start=datetime.fromtimestamp(0),
            stop=datetime.now(),
            bucket=self.bucket,
            org=self.org,
            predicate=predicate)
