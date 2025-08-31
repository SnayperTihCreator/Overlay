from pydantic import BaseModel, Field, BeforeValidator, ConfigDict
from typing import Annotated

from PySide6.QtCore import QPoint


def check_position(value):
    match value:
        case QPoint() as point:
            return point
        case [x, y]:
            return QPoint(x, y)
        case (x, y):
            return QPoint(x, y)
        case _:
            raise ValueError(f"Данный объект не представить как точку {value!r}")


class TestModel(BaseModel):
    position: Annotated[QPoint, BeforeValidator(check_position)]
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )
    
    
TestModel(position=[10, 10])
