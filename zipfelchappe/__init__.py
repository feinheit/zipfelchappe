
VERSION = (0, 3, 5)
__version__ = '.'.join(map(str, VERSION))


class PaymentProviderException(Exception):
    def __init__(self, message, *args, **kwargs):
        super(PaymentProviderException, self).__init__(message, *args, **kwargs)


payment_providers = {}

def register_provider(name, provider):
    payment_providers[name] = provider
