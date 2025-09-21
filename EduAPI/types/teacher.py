from dataclasses import dataclass


@dataclass
class Teacher:
    """Преподаватель"""

    name: str
    kaf: None
    id: int
    idFromRasp: bool

    def __init__(self, **kwargs):
        for field_name in self.__annotations__:
            setattr(self, field_name, kwargs.get(field_name))
