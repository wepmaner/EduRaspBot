from dataclasses import dataclass


@dataclass
class Audience:
    """Аудитория"""

    name: str
    id: int

    def __init__(self, **kwargs):
        for field_name in self.__annotations__:
            setattr(self, field_name, kwargs.get(field_name))
