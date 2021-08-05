import pytest

from ..address_validation_client.address_object.usps import USPSAddressObject, \
from ..address_validation_client.client import USPSClient
from ..address_validation_client.enums import USPSClientAPITypes
from ..address_validation_client.exceptions import AddressInvalidError


def test_address_validate() -> None:
    address_test_1 = USPSAddressObject(
        address_1="207 N Bowen", city="jackson", state="michigan", zip5="49202"
    )
    address_test_2 = USPSAddressObject(
        address_1="1301 Jones Street",
        address_2="Ste 15",
        city="Omaha",
        state="ne",
        zip5="68102",
    )

    usps_client = USPSClient(
        address=address_test_1, api_type=USPSClientAPITypes.VERIFY.value
    )
    test_1 = usps_client.validate_address()

    assert isinstance(test_1, USPSAddressObject)
    assert isinstance(test_1.address_1, str)
    assert isinstance(test_1.city, str)
    assert isinstance(test_1.state, str)
    assert isinstance(test_1.zip5, str)
    assert len(test_1.zip5) == 5

    usps_client = USPSClient(
        address=address_test_2, api_type=USPSClientAPITypes.VERIFY.value
    )
    test_2 = usps_client.validate_address()
    assert isinstance(test_2, USPSAddressObject)
    assert isinstance(test_2.address_1, str)
    assert isinstance(test_2.address_2, str)
    assert isinstance(test_2.city, str)
    assert isinstance(test_2.state, str)
    assert isinstance(test_2.zip5, str)
    assert len(test_2.zip5) == 5


def test_invalid_address():
    with pytest.raises(AddressInvalidError):
        address_test_invalid = USPSAddressObject(
            address_1="130123 Jones Street",
            address_2="Ste 12323",
            city="Omaha",
            state="CA",
            zip5="68102",
        )
        usps_client = USPSClient(
            address=address_test_invalid, api_type=USPSClientAPITypes.VERIFY.value
        )
        return usps_client.validate_address()


if __name__ == '__main__':
    test_address_validate()