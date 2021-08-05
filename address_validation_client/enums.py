from enum import Enum


class USPSClientEnums(Enum):
    USPSUserId = ""
    USPSUserPass = ""


class USPSClientAPITypes(Enum):
    VERIFY = "Verify"
    ZIP_LOOKUP = "ZipCodeLookup"
    CITY_STATE_LOOKUP = "CityStateLookup"


class USPSClientXMLTagVals(Enum):
    REVISION = "Revision"
    ADDRESS_VALIDATE_REQUEST = "AddressValidateRequest"
    ADDRESS_ELEMENT = "Address"
    ADDRESS_1 = "Address1"
    ADDRESS_2 = "Address2"
    CITY = "City"
    STATE = "State"
    ZIP5 = "Zip5"
    ZIP4 = "Zip4"
