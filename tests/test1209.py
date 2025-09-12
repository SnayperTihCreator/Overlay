from MinTools import OpenManager
from Service.metadata import metadata
import assets_rc

with OpenManager() as om:
    print(metadata("theme::Mocha"))