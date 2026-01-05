import toml

from pydantic import BaseModel


class BaseConfig(BaseModel):
    
    @classmethod
    def from_toml(cls, toml_data: str):
        return cls(**toml.loads(toml_data))
