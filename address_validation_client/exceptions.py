class Error(Exception):
    """Base class for other exceptions"""
    pass


class AddressInvalidError(Error):
    """Raised when address is not found by USPS API"""
    pass
