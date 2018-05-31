"""Lykke REST API backend.

Documentation:
- Public API: https://public-api.lykke.com/swagger/ui/index.html
- High-frequency trading API: https://hft-api.lykke.com/swagger/ui/
"""
# Import Built-ins
import logging

# Import Third-Party

# Import Homebrew
from bitex.api.REST import RESTAPI
from bitex.exceptions import IncompleteCredentialsError

log = logging.getLogger(__name__)


class LykkeREST(RESTAPI):
    """Lykke REST API class."""

    def __init__(self, addr=None, key=None, secret=None,
                 version=None, timeout=5, config=None):
        """Initialize the class instance."""
        addr = addr or 'https://hft-api.lykke.com/api'
        # The Lykke Wallet/HFT APIs need just a key
        secret = secret or 'not applicable'
        super(LykkeREST, self).__init__(addr=addr, version=version,
                                           key=key, secret=secret,
                                           timeout=timeout, config=config)

    def check_auth_requirements(self):
        """Check if authentication requirements are met."""
        try:
            super(LykkeREST, self).check_auth_requirements()
        except IncompleteCredentialsError:
            raise

    def load_config(self, fname):
        """Load configuration from a file."""
        conf = super(LykkeREST, self).load_config(fname)
        return conf

    def sign_request_kwargs(self, endpoint, **kwargs):
        """Sign the request."""
        req_kwargs = super(LykkeREST, self).sign_request_kwargs(endpoint, **kwargs)
        req_kwargs['headers'] = {'api-key': self.key}

        # Parameters go into the data kwarg, so move it there from 'params'
        # TODO : check if the following params are needed and implemented properly
        params = req_kwargs.pop('params')
        req_kwargs['data'] = params or req_kwargs['data']

        return req_kwargs
