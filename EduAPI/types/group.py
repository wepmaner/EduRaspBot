from dataclasses import dataclass


@dataclass
class Group:
    """Группа"""

    name: str
    id: int
    kurs: int
    facul: str
    yearName: str
    facultyID: int

    def __init__(self, **kwargs):
        for field_name in self.__annotations__:
            setattr(self, field_name, kwargs.get(field_name))
