import abc
from collections.abc import Callable
from typing import Any

class DB:
    @abc.abstractmethod
    def insert(self, table:str, properties:dict[str, Any]) -> None:
        pass
    @abc.abstractmethod
    def update(self, table:str, query:Any, properties:dict[str, Any]) -> None:
        pass
    @abc.abstractmethod
    def delete(self, table:str, query:Any) -> None:
        pass
    @abc.abstractmethod
    def query(self, table:str, query:Any) -> list[Any]:
        pass

class Dummy_DB(DB):

    def __init__(self) -> None:
        super().__init__()
        self.values = {}

    def insert(self, table: str, properties: dict[str, Any]):
        if not table in self.values:
            self.values[table] = []
        self.values[table].append(properties)

    def update(self, table: str, query: Any, properties: dict[str, Any]):
        assert isinstance(query, Callable), "dummyDB only support callable queries"

        for i in range(len(self.values[table])):
            if query(self.values[table][i]):
                for key in properties.keys():
                    self.values[table][i][key] = properties[key]

    def delete(self, table: str, query: Any):
        assert isinstance(query, Callable), "dummyDB only support callable queries"

        for i in reversed(range(len(self.values[table]))):
            if query(self.values[table][i]):
                del self.values[table][i]

    def query(self, table: str, query: Any):
        assert isinstance(query, Callable), "dummyDB only support callable queries"

        return_values = []
        for i in range(len(self.values[table])):
            if query(self.values[table][i]):
                return_values.append(self.values[table][i])
        return return_values


