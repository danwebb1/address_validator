from abc import abstractmethod
from urllib.parse import urlencode
from lxml import objectify

import urlfetch
from attrdict import AttrDict

from .address_object.usps import USPSAddressObject
from .enums import (
    USPSClientEnums,
    USPSClientAPITypes,
    USPSClientXMLTagVals,
)
from yattag import Doc, indent

from .exceptions import AddressInvalidError


class AddressValidationClient:
    def __init__(
        self, address: USPSAddressObject, api_type: USPSClientAPITypes
    ) -> None:
        """
        :param address: USPSAddressObjects
        :param api_type: USPSClientAPITypes
        """
        self.address = address
        self.api_type = api_type

    @abstractmethod
    def validate_address(self):
        """
        The main class method to build the payload, url, make the request and return the parsed response
        :return: dictionary of valid address
        """
        pass

    @staticmethod
    def _request_get(url: str) -> urlfetch.Response:
        """
        method to perform call to USPS API
        :param url: the url for the request
        :return JSON response or false if errors
        """
        response = urlfetch.fetch(
            url=url,
            method="GET",
            deadline=60,
            headers={"Content-Type": "application/xml"},
        )
        return response

    @abstractmethod
    def parse_response(self, response: urlfetch.Response):
        """
        parse response from API and return dict
        """
        pass


class USPSClient(AddressValidationClient):
    @property
    def api_signature(self) -> AttrDict:
        """
        the current CSG Actuarial USPS developer account user ID
        :return: string
        """
        return AttrDict(
            {
                "scheme": "https://",
                "host": "secure.shippingapis.com",
                "path": "/ShippingAPI.dll?API=",
            }
        )

    @property
    def user_id(self) -> str:
        """
        the current CSG Actuarial USPS developer account user ID
        :return: string
        """
        return USPSClientEnums.USPSUserId.value

    @property
    def revision(self) -> int:
        """
        Integer value used to return of all available response fields. Set this value to 1 to return all currently
        documented response fields.
        :return: int
        """
        return 1

    def __init__(
        self, address: USPSAddressObject, api_type: USPSClientAPITypes
    ) -> None:
        """
        :param address: USPSAddressObjects
        :param api_type: USPSClientAPITypes
        """
        self.address = address
        self.api_type = api_type
        super().__init__(self.address, self.api_type)


    def get_api_signature(self) -> None:
        """
        set the api type for the api signature
        :return None
        """
        signature = self.api_signature["api_type"]
        signature["api_type"] = self.api_type
        return signature

    def generate_xml(self) -> indent:
        """
        generate the xml for the request
        :return: yattag.indent
        """
        doc, tag, text = Doc().tagtext()
        with tag(
            USPSClientXMLTagVals.ADDRESS_VALIDATE_REQUEST.value,
            ("USERID", self.user_id),
        ):
            with tag(USPSClientXMLTagVals.REVISION.value):
                text(self.revision)
            with tag(USPSClientXMLTagVals.ADDRESS_ELEMENT.value, ("ID", 0)):
                with tag(USPSClientXMLTagVals.ADDRESS_1.value):
                    text(self.address.address_1)
                with tag(USPSClientXMLTagVals.ADDRESS_2.value):
                    text(self.address.address_2)
                with tag(USPSClientXMLTagVals.CITY.value):
                    text(self.address.city)
                with tag(USPSClientXMLTagVals.STATE.value):
                    text(self.address.state)
                with tag(USPSClientXMLTagVals.ZIP5.value):
                    text(self.address.zip5)
                with tag(USPSClientXMLTagVals.ZIP4.value):
                    text("")

        return doc.getvalue()

    def validate_address(self) -> USPSAddressObject:
        """
        The main class method to build the payload, url, make the request and return the parsed response
        :return: dictonary of
        """
        payload = urlencode({"XML": (self.generate_xml())})
        url = "{}{}{}{}&{}".format(
            self.api_signature.scheme,
            self.api_signature.host,
            self.api_signature.path,
            self.api_type,
            payload,
        )
        result = self._request_get(url=url)
        return self.parse_response(result)

    def parse_response(self, response: urlfetch.Response) -> USPSAddressObject:
        """
        parse response from USPS API and return dict
        :param response: urlfetch.Response
        :return: USPSAddressObject
        :raises TypeError | Exception
        """
        if response.status == 200:
            if isinstance(response.content, bytes):
                root = objectify.fromstring(response.content)
                try:
                    if root.Address.Error:
                        address_string = "{} {} {} {} {}".format(
                            self.address.address_1,
                            self.address.address_2,
                            self.address.city,
                            self.address.state,
                            self.address.zip5,
                        )
                        raise AddressInvalidError(
                            f"The address entered {address_string} was not found in the USPS database"
                        )
                except AttributeError:
                    pass
                try:
                    if root.Address.Address1:
                        address_1 = root.Address.Address1.text
                except AttributeError:
                    address_1 = ''

                return USPSAddressObject(
                    address_1=root.Address.Address2.text,  # address2 as returned by the usps api is correct here
                    address_2=address_1,                   # address1 as returned by the usps api is correct here
                    city=root.Address.City.text,
                    state=root.Address.State.text,
                    zip5=root.Address.Zip5.text,
                )
            else:
                _type = type(response.content)
                raise TypeError(f"expected type bytes but received {_type}")
        else:
            raise Exception(
                f"Received unexpected response code {response.status} when attempting to validate address"
            )
