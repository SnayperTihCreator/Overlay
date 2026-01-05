import re

from pydantic.dataclasses import dataclass
from pydantic import Field

from .base_config import BaseConfig

version_pattern = re.compile(r"(?P<ver>alpha|beta|release)?\s*"
                             r"(?P<v1>\d+)\.(?P<v2>\d+)\.(?P<v3>\d+)(?:\s*-\s*"
                             r"(?P<state>unstable|stable))?", re.I)
version_type = ["alpha", "beta", "release"]
version_state = ["unstable", "stable"]


@dataclass(frozen=True)
class MetaData:
    name: str = Field(default="<unknown>")
    version: str = Field(..., pattern=version_pattern)
    author: str = Field(default="<unknown>")
    description: str = Field(default="<no description>")


class CommonConfig(BaseConfig):
    metadata: MetaData = Field()
    
    def tuple_version(self):
        dv = self.dict_version()
        return (version_type.index(dv["ver"].lower()),
                int(dv["v1"]), int(dv["v2"]), int(dv["v3"]),
                version_state.index(dv["state"].lower()))
    
    def dict_version(self):
        return version_pattern.fullmatch(self.metadata.version).groupdict()