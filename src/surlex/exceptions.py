class SurlexException(Exception):
    """
        a generic surlex exception
    """
    pass

class MalformedSurlex(SurlexException):
    """
        surlex parser error -- when read_until does not find
        the expected character it'll throw this
    """
    pass

class MacroDoesNotExist(SurlexException):
    """
        surlex parser error -- when a macro cannot be resolved
        this will be thrown
    """
    pass
