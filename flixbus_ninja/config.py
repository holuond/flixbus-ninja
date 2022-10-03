from dataclasses import dataclass
from typing import Dict

import dataconf
import yaml


@dataclass
class Config:
    departure_city: str
    departure_station: str
    departure_date: str
    departure_times_ordered_by_priority: list[str]
    destination_city: str
    destination_station: str
    passengers: Dict[str, int]

    @classmethod
    def from_yaml(cls, filepath):
        with open(filepath, 'r', encoding='utf-8') as file:
            return dataconf.dict(yaml.safe_load(file), cls)

        # dataconf.file(filepath, cls) # the yaml parsing corrupted some Unicode chars (can't set an explicit encoding)
