from MinTools import OpenManager
from Service.metadata import metadata

with OpenManager() as om:
    print(metadata("theme::Mocha"))