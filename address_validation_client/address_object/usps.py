import typing
from pydantic import BaseModel


class USPSAddressObject(BaseModel):
    address_1: str
    city: str
    state: str
    zip5: str
    address_2: typing.Optional[str] = ""
